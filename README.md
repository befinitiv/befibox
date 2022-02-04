# Introduction

This repository hold the code and mechanics for the DIY Youtube Music Player Box.
The root folder contains everything needed to install this on a Raspberry. In addition to that, you'll also find the folder "tag_creator" that contains a Python script for generating paper templates for Youtube QR tags with thumbnails.
The mech folder contains the OpenSCAD mechanic designs together with some random example tags models.

# Installation
	scp qr.py qr.service requirements.txt configs/mopidy.conf configs/config.txt pi@192.168.1.XXX:/tmp
	ssh pi@192.168.1.XXX

	pip install -r /tmp/requirements.txt
	sudo cp /tmp/mopidy.conf /etc/mopidy
	sudo cp /tmp/config.txt /boot/config.txt # This enables PWM audio output on RPI Zero
	sudo cp /tmp/qr.service /etc/systemd/system
	cp /tmp/qr.py /home/pi

	sudo systemctl enable qr

# Usage

Put a Youtube URL (or Webradio or whatever) into a QR code and put it onto the box -> Video should be played.

Please note that playing a video for the first time takes some moments because it first needs to be downloaded. After this the video will play immediately since it will be cached.
