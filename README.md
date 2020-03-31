# Therapy Pet Robot 
UG4 HONOURS PROJECT FOR ACADEMIC YEAR 2019-2020

[Video](https://www.youtube.com/watch?v=2LshSIcbxts&t=2s)

## Step 1 :
Install required libraries
- RPi.GPIO
- pygame
- numpy

## Step 2 :
Connect all GPIO pins to pi
- Left capacitive touch sensor pin = 17
- Right capacitive touch sensor pin = 18
- Servo motor pin = 14
- Vibration motor pin = 21

 A digram of the pins can be found [here](https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.raspberrypi-spy.co.uk%2F2012%2F06%2Fsimple-guide-to-the-rpi-gpio-header-and-pins%2F&psig=AOvVaw16_Ydvoo0D2PYr64OJ9Y33&ust=1585741021852000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCLDi0OTPxOgCFQAAAAAdAAAAABAD)

## Step 3 :
Run robot module:

$ python Robot/robot.py

If you want the robot to initialize its state run:

$ python Robot/robot.py init
