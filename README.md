# Chatterbox 

## Aim:

A probably outdated-by-now project to create OpenAI assistants with access to manuals for equipment like 3d-printers in order to make it easier and funner for new users to learn to use said equipment. Bonus addition of voice effects to differentiate the voices a bit from stock open-AI voices. 

In many ways, this project is like a home assistant speaker box. While an internet/phone application would likely be the best implimentation of such a concept from a cost perspective, I started doing this and had a bit of fun learning along the way. 

This is similar to the chatbot designed by [pdp12](https://www.instructables.com/Customizes-a-ChatGPT-Assistant-Using-a-RaspberryPi/). In this case I am making a hobbyist hat for a raspberry pi zero two W.

## Assumed Knowledge:
It is assumed that you are comfortable with soldering, hooking together breakout dev boards for chips, using a raspberry Pi OS and/or SSH and python programming.

## Hardware:
![image of a Raspberry Pi Zero Two W with many rainbow ribbon innie-to-innie cables connecting a computer key switch, a DAC amp, a 3W speaker, and an I2S MEMS Microphone V1.0]()

## To use:
Use the Raspberry Pi Imager to load the OS onto the Raspberry Pi Zero Two W.

An OpenAI account and subsquent API key is required.
Save your API details into the .env file


## Code:
The code sets up 

##To do: 
The ability to close old threads and start new threads would be nice
The addition of status LEDs would be great, which I think has to be handled by a smaller microcontroller like an ATtiny.
