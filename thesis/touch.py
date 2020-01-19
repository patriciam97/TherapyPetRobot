import RPi.GPIO as GPIO
import pygame
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading
from sounds import get_sound 

# set up of pins
touch = 14
motor = 15
distance_echo = 20
distance_trigger = 16
vibration_sensor = 21
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(motor,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setup(distance_echo,GPIO.IN)
GPIO.setup(distance_trigger,GPIO.OUT)
GPIO.setup(vibration_sensor, GPIO.IN)
p = GPIO.PWM(motor, 50)     # Sets up pin 11 as a PWM pin
p.start(0)                  # Starts running PWM on the pin and sets it to 0

# initial state
overall_state = {"state":2,"sensor_moved": False, "last_pet":time.time(),"last_moved": time.time(), "touchstatus":False, "alternate": False, "motor": p,"music_busy":False,"music_writing":None}

def callback_vibration(channel):
    # Detects movement from vibration sensors
        if GPIO.input(channel):
                print ("Movement Detected!")
        else:
                print ("Movement Detected!")

GPIO.add_event_detect(vibration_sensor, GPIO.BOTH, bouncetime=300)  # let us know when the pin 26 goes HIGH or LOW
GPIO.add_event_callback(vibration_sensor, callback_vibration)  # assign function to GPIO PIN 26, Run function on change

def handle_barks(state):
    global overall_state
    overall_state["music_writing"]=state
    get_sound.get_new_sound(state)
    overall_state["music_writing"]=None
    print("Sound for state"+state+" updated.")

def bark():
    global overall_state
    if overall_state["music_writing"]!= overall_state["state"]:
        overall_state["music_busy"] = not overall_state["music_busy"]
        current_state = overall_state["state"]
        pygame.mixer.init()
        title = "/home/pi/Documents/TherapyPetRobot/thesis/sounds/new/sound_"+str(overall_state["state"])+".wav"
        pygame.mixer.music.load(title)  
        pygame.mixer.music.play()
        pygame.mixer.music.fadeout(1000)
        overall_state["music_busy"] = not overall_state["music_busy"]
        new_barks_thread = threading.Thread(target=handle_barks,args=(current_state,))
        new_barks_thread.start()

    

def handle_state():
    global overall_state
    while True:
        if time.time()-overall_state["last_pet"]>20 and overall_state["state"]>2:
            # every 20 second state drops
            overall_state["state"]-=1
            print("State dropped to "+str(overall_state["state"]))

def distance_sensor():
    # function to detect objects within an x distance
    while True:
        GPIO.output(distance_trigger,True)
        time.sleep(0.5)
        GPIO.output(distance_trigger,False)
        start_time = time.time()
        stop_time = time.time()
        while GPIO.input(distance_echo) == 0:
            start_time = time.time()
        while GPIO.input(distance_echo) == 1:
            stop_time = time.time()
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300)/2
        # # print(distance)
        # if distance <= 50 and overall_state["music_busy"] == False:
        #     bark_thread = threading.Thread(target=bark)
        #     bark_thread.start()
        #     time.sleep(0.3)

def set_tail_angle(angle):
    global overall_state
    duty = angle / 18 + 2
    overall_state["motor"].ChangeDutyCycle(duty)
    sleep(0.5)

def move_tail():
    global overall_state
    randtime = random.randint(4,10)
    if overall_state["music_busy"] == False:
        bark_thread = threading.Thread(target=bark)
        bark_thread.start()
    while randtime > 0:
        print(randtime)
        overall_state["touchstatus"] = not overall_state["touchstatus"]
        set_tail_angle(0 if overall_state["alternate"] else 90)
        overall_state["alternate"]= not overall_state["alternate"]
        randtime-=1
        time.sleep(0.5)

def automatic():
    global overall_state
    while True:
        if overall_state["sensor_moved"]:
            time.sleep(1)
            continue
        if time.time() - overall_state["last_moved"] > 7:
            print("GO CRAZY")
            move_tail()
            time.sleep(2)
            overall_state["last_moved"] = time.time()
        time.sleep(0.05)
        # print("Waiting...")

def read_touchsensor():
    global alternate, overall_state, touch
    while True:
        if (GPIO.input(touch)):
            overall_state["sensor_moved"] = True
            move_tail()
            overall_state["sensor_moved"] = False
            overall_state["last_moved"] = time.time()
            overall_state["last_pet"]= time.time()
            if overall_state["state"]<7:
                overall_state["state"] = overall_state["state"]+1
                print("State increased to "+str(overall_state["state"]))
        time.sleep(0.02)

def main():
     state_thread = threading.Thread(target=handle_state)
     distance_thread = threading.Thread(target=distance_sensor)
     automatic_thread = threading.Thread(target=automatic)
     state_thread.start()
     automatic_thread.start()
     distance_thread.start()
     read_touchsensor()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
    else:
        p.stop()
        GPIO.cleanup()
