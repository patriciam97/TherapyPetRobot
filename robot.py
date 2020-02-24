import RPi.GPIO as GPIO
import pygame
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading
import get_sound2
import numpy as np

left_capacitive_touch_sensor_pin = 17
right_capacitive_touch_sensor_pin = 18
servo_motor_pin = 14
vibration_motor_pin = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.setup(servo_motor_pin,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)

GPIO.setup(vibration_motor_pin,GPIO.OUT)
GPIO.output(vibration_motor_pin,GPIO.LOW)


p = GPIO.PWM(servo_motor_pin, 50)     # Sets up pin 11 as a PWM pin
p.start(0)                  # Starts running PWM on the pin and sets it to 0

overall_state = {"just_started":True,"state":0,"tail_moves": False, "last_pet":time.time(),"last_tail_moved": time.time(), "touchstatus":False, "tail_alternate": False, "motor": p,"music_busy":False,"music_writing":None,"last_bark":time.time(),"bark":False,"heartbeat":False}
thread_state= {"main_running": False, "state_thread":None,"bark_thread":None,"left_touch_sensor_thread":None,"right_touch_sensor_thread":None}

def handle_state():
    global overall_state, thread_state
    while thread_state["main_running"]:
        secs = random.randint(50, 200)
        if time.time()-overall_state["last_pet"]>secs and overall_state["state"]>1:
            # every 20 second state drops
            overall_state["state"]-=1
            print("State dropped to "+str(overall_state["state"]))
        time.sleep(2)


def set_tail_angle(angle):
    global overall_state
    duty = angle / 18 + 2
    overall_state["motor"].ChangeDutyCycle(duty)
    sleep(0.5)

def move_tail():
    global overall_state,thread_state
    randtime = random.randint(4,10)
    # overall_state["music_busy"]=not overall_state["music_busy"]
    overall_state["tail_moves"] = True
    while (thread_state["main_running"] and randtime > 0):
        print(randtime)
        # overall_state["touchstatus"] = not overall_state["touchstatus"]
        set_tail_angle(90 if overall_state["tail_alternate"] else 0)
        # set_tail_angle(10 if overall_state["tail_alternate"] else 90)
        overall_state["tail_alternate"]= not overall_state["tail_alternate"]
        randtime-=1
        time.sleep(0.5)
    overall_state["last_tail_moved"] = time.time()
    overall_state["music_busy"] = False
    overall_state["bark"] = False
    overall_state["tail_moves"] = False

def automatic_tail():
    global overall_state, thread_state
    while thread_state["main_running"]:
        if overall_state["tail_moves"]:
            time.sleep(1)
            continue
        if time.time() - overall_state["last_tail_moved"] > 15:
            print("GO CRAZY")
            overall_state["bark"]= True
            overall_state["heartbeat"]= False
            move_tail()
            time.sleep(2)
            overall_state["last_tail_moved"] = time.time()
            continue
        time.sleep(0.2)
        print("Waiting...")

def read_left_touchsensor():
    global overall_state,left_capacitive_touch_sensor_pin, thread_state
    while thread_state["main_running"]:
        if (GPIO.input(left_capacitive_touch_sensor_pin) and overall_state["bark"]==False and overall_state["heartbeat"]==False ):
            print("touched")
            if overall_state["state"]<6 and time.time() - overall_state["last_tail_moved"]>2:
                print("State increased to "+str(overall_state["state"]))
                overall_state["state"]+=1
            bark_sound_probability = np.random.choice(["bark","heartbeat"],p=[0.7,0.3])
            print(bark_sound_probability)
            if (bark_sound_probability == "bark"):
                overall_state["bark"]= True
                overall_state["heartbeat"]= False
                move_tail()
            else:
                overall_state["heartbeat"]= True
                overall_state["bark"]= False
        time.sleep(0.2)

def read_right_touchsensor():
    global overall_state,right_capacitive_touch_sensor_pin, thread_state,vibration_motor_pin
    while thread_state["main_running"]:
        if (GPIO.input(right_capacitive_touch_sensor_pin) and overall_state["bark"]==False and overall_state["heartbeat"]==False ):
            # and  overall_state["bark"]==False not overall_state["heartbeat"]==False
            print("touched")
            if overall_state["state"]<6 and time.time() - overall_state["last_tail_moved"]>2:
                print("State increased to "+str(overall_state["state"]))
                overall_state["state"]+=1
            bark_sound_probability = np.random.choice(["bark","heartbeat"],p=[0.7,0.3])
            print(bark_sound_probability)
            if (bark_sound_probability == "bark"):
                overall_state["bark"]= True
                overall_state["heartbeat"]= False
                move_tail()
            else:
                overall_state["heartbeat"]= True
                overall_state["bark"]= False
        time.sleep(0.2)

def handle_barks(state):
    global overall_state
    overall_state["music_writing"] = state
    get_sound2.get_new_sound(state)
    overall_state["music_writing"] = None
    print("Sound for state "+str(state)+" updated.")

def heartbeat_vibration():
    global overall_state, thread_state
    while thread_state["main_running"]:
        if (overall_state["heartbeat"]):
            time.sleep(0.05)
            GPIO.output(vibration_motor_pin,GPIO.HIGH)
            time.sleep(0.40)
            print("stop vibration")
            GPIO.output(vibration_motor_pin,GPIO.LOW)
            time.sleep(0.2)
        else:
            GPIO.output(vibration_motor_pin,GPIO.LOW)


def heartbeat_sound():
    global overall_state, thread_state
    while thread_state["main_running"]:
        if (overall_state["heartbeat"] and not overall_state["music_busy"]):
            overall_state["music_busy"] = True
            title = "/home/pi/Documents/TherapyPetRobot/sounds/heartbeat2"+".wav"
            pygame.mixer.music.load(title)
            pygame.mixer.music.set_volume(100)
            pygame.mixer.music.play()
            time.sleep(random.randint(5, 10))
            overall_state["music_busy"] = False
            overall_state["heartbeat"]= False
            print("Heartbeat: "+str(overall_state["heartbeat"]))
            



def bark():
    global overall_state, thread_state
    while thread_state["main_running"]:
        if (overall_state["bark"] and overall_state["state"] in range(0,7) and(overall_state["music_writing"] != overall_state["state"]) and not overall_state["music_busy"]):
            print("Current state: "+str(overall_state["state"]))
            overall_state['last_bark']=time.time()
            overall_state["music_busy"] = True
            current_state = overall_state["state"]
            title = "/home/pi/Documents/TherapyPetRobot/sounds/new/sound_"+str(overall_state["state"])+".wav"
            pygame.mixer.music.load(title)  
            new_barks_thread = threading.Thread(target=handle_barks,args=(current_state,))
            new_barks_thread.start()
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play()
            # pygame.mixer.music.fadeout(100)
            # while pygame.mixer.music.get_busy:
            #     pass
                # print("barking sound")
            # time.sleep(random.randint(10, 20))
            # overall_state["music_busy"] = False
            # overall_state["bark"] = False
            # overall_state["tail_moves"] = False
def main():
    global thread_state
    thread_state["main_running"] = True
    automatic_thread = threading.Thread(target=automatic_tail)
    automatic_thread.start()

    state_thread = threading.Thread(target=handle_state)
    thread_state["state_thread"]=state_thread
    state_thread.start()

    bark_thread = threading.Thread(target=bark)
    thread_state["bark_thread"]=bark_thread
    bark_thread.start()

    left_touch_sensor_thread = threading.Thread(target = read_left_touchsensor)
    thread_state["left_touch_sensor_thread"]=left_touch_sensor_thread
    left_touch_sensor_thread.start()
    
    right_touch_sensor_thread = threading.Thread(target = read_right_touchsensor)
    thread_state["right_touch_sensor_thread"]=right_touch_sensor_thread
    right_touch_sensor_thread.start()

    heartbeat_sound_thread = threading.Thread(target = heartbeat_sound)
    thread_state["heartbeat_sound_thread"]=heartbeat_sound_thread
    heartbeat_sound_thread.start()

    heartbeat_vibration_thread = threading.Thread(target = heartbeat_vibration)
    thread_state["heartbeat_vibration_thread"]=heartbeat_vibration_thread
    heartbeat_vibration_thread.start()
    
    while True:
        if overall_state["just_started"]:
            overall_state["bark"]=True
            time.sleep(4)
            overall_state["bark"]=False
            overall_state["music_busy"]= False
            overall_state["just_started"]= False
        # GPIO.output(vibration_motor_pin,GPIO.HIGH)
        # time.sleep(10000)
        # print("stop vibration")
        # GPIO.output(vibration_motor_pin,GPIO.LOW)
        # time.sleep(2000000)
        # print(overall_state["music_busy"])
        time.sleep(1)

if __name__ == '__main__':
    try:
        pygame.mixer.init()
        f = open("state.txt","r")
        contents = f.read()
        line1 = contents.split("\n")[0]
        line2 = contents.split("\n")[1]
        overall_state["state"]=int(line1.split(":")[1])
        overall_state["tail_alternate"]=bool(line2.split(":")[1])
        main()
    except KeyboardInterrupt:
        f= open("state.txt","w")
        f.write("state: "+str(overall_state["state"]))
        f.write("\ntail_alternate: "+str(overall_state["tail_alternate"]))
        f.close()
        overall_state["music_busy"] = False
        overall_state["bark"] = False
        overall_state["heartbeat"] = False
        pygame.mixer.music.stop()
        thread_state["main_running"] = False
        for state in range(7):
            get_sound2.get_new_sound(state)
        p.stop()
        GPIO.cleanup()
    else:
        p.stop()
        GPIO.cleanup()
