import RPi.GPIO as GPIO
import pygame
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading

left_capacitive_touch_sensor_pin = 15
right_capacitive_touch_sensor_pin = 18
servo_motor_pin = 14

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.setup(servo_motor_pin,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)

p = GPIO.PWM(servo_motor_pin, 50)     # Sets up pin 11 as a PWM pin
p.start(0)                  # Starts running PWM on the pin and sets it to 0

overall_state = {"state":5,"tail_moves": False, "last_pet":time.time(),"last_tail_moved": time.time(), "touchstatus":False, "tail_alternate": False, "motor": p,"music_busy":False,"music_writing":None,"last_bark":time.time()}


def handle_state():
    global overall_state
    while True:
        if time.time()-overall_state["last_pet"]>20 and overall_state["state"]>1:
            # every 20 second state drops
            overall_state["state"]-=1
            print("State dropped to "+str(overall_state["state"]))


def set_tail_angle(angle):
    global overall_state
    duty = angle / 18 + 2
    overall_state["motor"].ChangeDutyCycle(duty)
    sleep(0.5)

def move_tail():
    global overall_state
    randtime = random.randint(4,10)
    overall_state["music_busy"]=not overall_state["music_busy"]
    while randtime > 0:
        print(randtime)
        overall_state["touchstatus"] = not overall_state["touchstatus"]
        set_tail_angle(0 if overall_state["tail_alternate"] else 90)
        overall_state["tail_alternate"]= not overall_state["tail_alternate"]
        randtime-=1
        time.sleep(0.5)
    overall_state["music_busy"] = not overall_state["music_busy"]

def automatic_tail():
    global overall_state
    while True:
        if overall_state["tail_moves"]:
            time.sleep(1)
            continue
        if time.time() - overall_state["last_tail_moved"] > 15:
            print("GO CRAZY")
            move_tail()
            time.sleep(2)
            overall_state["last_tail_moved"] = time.time()
        time.sleep(0.05)
        print("Waiting...")

def read_left_touchsensor():
    global overall_state
    while True:
        if (GPIO.input(left_capacitive_touch_sensor_pin)):
            print("touched")
            if overall_state["state"]<10:
                overall_state["state"]+=1
            overall_state["tail_moves"] = True
            move_tail()
            overall_state["tail_moves"] = False
            overall_state["last_tail_moved"] = time.time()
        time.sleep(0.02)

def read_right_touchsensor():
    global overall_state
    while True:
        if (GPIO.input(right_capacitive_touch_sensor_pin)):
            print("touched")
            if overall_state["state"]<10:
                overall_state["state"]+=1
            overall_state["tail_moves"] = True
            move_tail()
            overall_state["tail_moves"] = False
            overall_state["last_tail_moved"] = time.time()
        time.sleep(0.02)

def main():

    # automatic_thread = threading.Thread(target=automatic_tail)
    # automatic_thread.start()


    left_touch_sensor_thread = threading.Thread(target = read_left_touchsensor)
    left_touch_sensor_thread.start()
    
    right_touch_sensor_thread = threading.Thread(target = read_right_touchsensor)
    right_touch_sensor_thread.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
    else:
        p.stop()
        GPIO.cleanup()
