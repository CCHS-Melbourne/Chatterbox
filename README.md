# Chatterbox 

## Aim:

A project to connect Push-to-talk OpenAI assistants with access to manuals for equipment like 3d-printers in order to make it easier and funner for new users to learn to use said equipment. Bonus addition of voice effects to differentiate the voices a bit from stock open-AI voices. 

This is similar to the chatbot designed by [pdp12](https://www.instructables.com/Customizes-a-ChatGPT-Assistant-Using-a-RaspberryPi/). In this case I am making a hobbyist hat for a raspberry pi zero two W.

## Assumed Knowledge:
It is assumed that you are comfortable with soldering, hooking together breakout dev boards for chips, using a raspberry Pi OS and/or SSH and python programming.

## Hardware:
The hardward used to build this project may be found here: [PancakeLegend/ChatterBox](https://github.com/PancakeLegend/ChatterBox), modified top plate and housing can be found in branch here: [GoatNote/ChatterBox](https://github.com/GoatNote/ChatterBox-1)

![Raspberry Pi Zero Two W with a hat containing a DAC amp, a 3W speaker, and an I2S MEMS Microphone V1.0](.jpg)

## To use:
Use the Raspberry Pi Imager to load the OS onto the Raspberry Pi Zero Two W.

An OpenAI account and subsquent API key is required.
Save your API details into the .env file

# PI Setup
First you need to modify the /boot/firmaware/config.txt file to enable the I2S audio and the I2C bus. 
You need to uncomment dtparam=i2s=on and dtparam=i2c_arm=on
you need to add: 
````
dtoverlay=googlevoicehat-soundcard
````


## Code:
This code needs to be cloned and put on the Raspberry Pi Zero Two W.
You will need to then install the required libraries with the following command:


```
sudo apt install libasound2-dev
sudo apt install libportaudio2
sudo apt update
sudo apt pulseaudio
sudo apt portaudio19-dev
sudo apt python3-dev

sudo apt install git
git clone https://github.com/CCHS-Melbourne/Chatterbox.git

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Setup for auto-starting on boot: 
The chatter.service file is a systemd service file that will start the chatterbox on boot.

You will first need to make the chatter.service file executable with the following command:
```
chmod +x chatter.service
chmod +x start.sh
```

To have it auto-start on boot, you need to add the chatter.service to the /etc/systemd/user directory.

If your user for the pi is not chatter2 you will need to modify the following lines int eh chatter.service file:
Environment="USER=chatter2"         # the user you want to run the service as
Environment="HOME=/home/chatter2"   # the home directory of the user
ExecStart="/home/chatter2/Chatterbox/start.sh" # location of the start.sh file

Then as the user you want to run the service, enable the service with the following command:
```
systemctl --user enable chatter.service
```

You will also need to make sure the user is logged in automatically on boot. You do this by going to the Raspberry Pi Configuration tool and setting the user to auto-login.
```
sudo raspi-config
```
System Options -> Boot / Auto Login -> Console Autologin

## To do: 
The ability to close old threads and start new threads would be nice
Stream the audio to the API to speed up the processing times.
