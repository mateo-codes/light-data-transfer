10/14/2026

This was a project to understand how data can be transmitted as light. The setup was a red led
controlled by an esp32. The data was sent as hex with a start header and length of the message,
followed by the data bits enocded into hex. 
A photoresistor was connected to our pi on pin 17. We then read the bits and decode it back.

Worked well but the led and photoresistor needed to be within a inch of eachother for this to work.
We can also only do 10 bits per second, so transmission is slow but reliable. 

This was done as a way to understand fiber optics and how data is transmitted by light. 
Cool concept :p

- mateoCodes
