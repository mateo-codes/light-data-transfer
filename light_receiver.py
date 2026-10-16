#!/usr/bin/env python3
"""
Light receiver for the Raspberry Pi.
Reads bits from the photoresistor divider on GPIO 17 and saves what it receives.

Protocol (must match the ESP32 sketch):
  idle = light OFF
  each byte = 1 start bit (light ON) + 8 data bits (LSB first) + stop bit (light OFF)
  message  = 0xAA 0x55 | length (2 bytes, high first) | data | checksum (sum of data mod 256)
"""
import time
from gpiozero import DigitalInputDevice

BIT_TIME = 0.100        # seconds per bit -- must match BIT_MS on the ESP32 (100 ms)
PIN = 17
OUTFILE = "received.bin"

sensor = DigitalInputDevice(PIN, pull_up=False)


def wait_until(t):
    while time.monotonic() < t:
        time.sleep(0.001)


def read_byte(timeout=None):
    """Wait for a start bit (light ON), then sample 8 data bits in the middle of each bit."""
    start = time.monotonic()
    while not sensor.value:
        if timeout and time.monotonic() - start > timeout:
            return None
        time.sleep(0.001)

    edge = time.monotonic()
    value = 0
    for i in range(8):
        wait_until(edge + BIT_TIME * (1.5 + i))   # middle of data bit i
        if sensor.value:
            value |= 1 << i
    wait_until(edge + BIT_TIME * 9.5)             # middle of the stop bit
    return value


def main():
    print(f"Listening on GPIO {PIN} at {1 / BIT_TIME:.0f} bits/sec...")
    while True:
        # 1. Find the sync header 0xAA 0x55
        prev = None
        while True:
            b = read_byte()
            print(hex(b), end= " ", flush=True)
            if prev == 0xAA and b == 0x55:
                break
            prev = b

        # 2. Read the length
        hi, lo = read_byte(5), read_byte(5)
        if hi is None or lo is None:
            print("Lost signal reading length, waiting for next header.")
            continue
        length = (hi << 8) | lo
        print(f"Receiving {length} bytes (about {length * 11 * BIT_TIME:.0f} s)")

        # 3. Read the data
        data = bytearray()
        for n in range(length):
            b = read_byte(timeout=5)
            if b is None:
                print("\nTimed out mid-message.")
                break
            data.append(b)
            print(f"\r{n + 1}/{length}  {data[-40:].decode('ascii', 'replace')}", end="", flush=True)
        print()

        # 4. Check and save
        checksum = read_byte(5)
        ok = checksum == (sum(data) & 0xFF)
        print("Checksum OK" if ok else f"Checksum FAILED (got {checksum}, expected {sum(data) & 0xFF})")
        with open(OUTFILE, "wb") as f:
            f.write(data)
        print(f"Saved to {OUTFILE}\n")


if __name__ == "__main__":
    main()
