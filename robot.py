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

overall_state = {"just_started":True,"state":0,"tail_moves": False,"tail_angle":0, "last_pet":time.time(),"last_tail_moved": time.time(), "touchstatus":False, "tail_alternate": False, "motor": p,"music_busy":False,"music_writing":None,"last_bark":time.time(),"bark":False,"heartbeat":False,"touch_counter":1}
thread_state= {"main_running": False, "state_thread":None,"bark_thread":None,"left_touch_sensor_thread":None,"right_touch_sensor_thread":None}
tail_movement_steps= [6,5,4,3,2,1,1]
def handle_state():
    global overall_state, thread_state
    while thread_state["main_running"]:
        secs = random.randint(60, 420) #1min to 7 mins
        if time.time()-overall_state["last_pet"]>secs and overall_state["state"]>1:
            overall_state["state"]-=1
            print("State dropped to "+str(overall_state["state"]))
        time.sleep(2)


def set_tail_angle(angle):
    global overall_state
    duty = angle / 18 + 2
    overall_state["motor"].ChangeDutyCycle(duty)
    overall_state["tail_angle"] = angle
    # sleep(0.5)

def move_tail():
    global overall_state,thread_state, tail_movement_steps
    randtime = random.randint(4,10)
    overall_state["tail_moves"] = True
    print("State: "+ str(overall_state["state"]))
    while (thread_state["main_running"] and randtime > 0):
        # set_tail_angle(90 if overall_state["tail_alternate"] else 0)
        # overall_state["tail_alternate"]= not overall_state["tail_alternate"]
        # randtime-=1
        # time.sleep(0.5)
        servo_position = overall_state["tail_angle"]
        # servo_position = 0
        target = 110 if overall_state["tail_alternate"] else 0
        speed = (abs(target - servo_position)) // int(tail_movement_steps[(overall_state["state"])])
        last_speed = (abs(target - servo_position)) % int(tail_movement_steps[(overall_state["state"])])
        # print(speed,last_speed)
        # speed = 10
        # print("moving from "+ str(servo_position) +" to "+str(target) +" step: "+str(speed))
        while( thread_state["main_running"] and servo_position!=target):
            if(servo_position <= target):
                servo_position += speed
            if(servo_position > target):
                servo_position -= speed
            if(abs(servo_position - target)<speed):
                servo_position = target
            set_tail_angle(servo_position)
            time.sleep(0.001)
        # print(randtime)
        randtime-=1
        overall_state["tail_alternate"]= not overall_state["tail_alternate"]
        time.sleep(1)
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
        if (time.time() - overall_state["last_pet"] > 60) and (overall_state["bark"]==False and overall_state["heartbeat"]==False ):
            bark_sound_probability = np.random.choice(["bark","heartbeat"],p=[0.8,0.2])
            print("Starting : "+bark_sound_probability)
            if (bark_sound_probability == "bark"):
                overall_state["bark"]= True
                overall_state["heartbeat"]= False
                move_tail()
            else:
                overall_state["heartbeat"]= True
                overall_state["bark"]= False
                overall_state["last_pet"] = time.time()
        time.sleep(0.2)
        # print("Waiting...")

def read_left_touchsensor():
    global overall_state,left_capacitive_touch_sensor_pin, thread_state
    while thread_state["main_running"]:
        if (GPIO.input(left_capacitive_touch_sensor_pin) and overall_state["bark"]==False and overall_state["heartbeat"]==False ):
            print("Left hand touch sensor: Enabled")
            if overall_state["state"]<6 and overall_state["touch_counter"]==0:
                print("State increased to "+str(overall_state["state"]))
                overall_state["state"]+=1
                overall_state["touch_counter"] = random.randint(3,9)
            bark_sound_probability = np.random.choice(["bark","heartbeat"],p=[0.8,0.2])
            print("Starting : "+bark_sound_probability)
            if (bark_sound_probability == "bark"):
                overall_state["bark"]= True
                overall_state["heartbeat"]= False
                move_tail()
            else:
                overall_state["heartbeat"]= True
                overall_state["bark"]= False
            overall_state["touch_counter"]-=1
        time.sleep(0.2)

def read_right_touchsensor():
    global overall_state,right_capacitive_touch_sensor_pin, thread_state,vibration_motor_pin
    while thread_state["main_running"]:
        if (GPIO.input(right_capacitive_touch_sensor_pin) and overall_state["bark"]==False and overall_state["heartbeat"]==False ):
            print("Right hand touch sensor: Enabled")
            if overall_state["state"]<6 and overall_state["touch_counter"]==0:
                print("State increased to "+str(overall_state["state"]))
                overall_state["state"]+=1
                overall_state["touch_counter"] = random.randint(3,9)
            bark_sound_probability = np.random.choice(["bark","heartbeat"],p=[0.8,0.2])
            print("Starting : "+bark_sound_probability)
            if (bark_sound_probability == "bark"):
                overall_state["bark"]= True
                overall_state["heartbeat"]= False
                move_tail()
            else:
                overall_state["heartbeat"]= True
                overall_state["bark"]= False
            overall_state["touch_counter"]-=1
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
            try:
                title = "/home/pi/Documents/TherapyPetRobot/sounds/new/sound_"+str(overall_state["state"])+".wav"
                a = pygame.mixer.Sound(title)
                pygame.mixer.Sound.play(a,fade_ms=2000)
                pygame.mixer.music.fadeout(2000)
                new_barks_thread = threading.Thread(target=handle_barks,args=(current_state,))
                new_barks_thread.start()
                pygame.mixer.music.set_volume(1)
                if (a.get_length()>3):
                    sleep_counter = random.randint(3, int(a.get_length()))
                else:
                    sleep_counter = 3
                print(sleep_counter)
                time.sleep(sleep_counter)
                print("DONE")
                overall_state["music_busy"] = False
                overall_state["bark"] = False
                overall_state["tail_moves"] = False
            except:
                for state in range(7):
                    get_sound2.get_new_sound(state)

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
            overall_state["just_started"]= False
        print("music busy: "+ str(overall_state["music_busy"])+" bark: "+ str(overall_state["bark"])+" heartbeat: "+ str(overall_state["heartbeat"]))
        time.sleep(1)

if __name__ == '__main__':
    try:
        pygame.mixer.init()
        f = open("state.txt","r")
        contents = f.read()
        line1 = contents.split("\n")[0]
        line2 = contents.split("\n")[1]
        line2 = contents.split("\n")[2]
        overall_state["state"]=int(line1.split(":")[1])
        overall_state["tail_alternate"]=bool(line2.split(":")[1])
        overall_state["tail_angle"] = int(line1.split(":")[1])
        # set_tail_angle(0)
        # time.sleep(3)
        main()
    except KeyboardInterrupt:
        f= open("state.txt","w")
        f.write("state: "+str(overall_state["state"]))
        f.write("\ntail_alternate: "+str(overall_state["tail_alternate"]))
        f.write("\ntail_angle: "+str(overall_state["tail_angle"]))
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
