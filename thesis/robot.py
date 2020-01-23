import RPi.GPIO as GPIO
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading
import get_sound 

capacitive_touch_sensor_pin = 2
servo_motor_pin = 3
distance_echo_pin = 14
distance_trigger_pin = 15
vibration_sensor = 26
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setup(capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(servo_motor_pin,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setup(distance_echo_pin,GPIO.IN)
GPIO.setup(distance_trigger_pin,GPIO.OUT)
GPIO.setup(vibration_sensor, GPIO.IN)
p = GPIO.PWM(servo_motor_pin, 50)     # Sets up pin 11 as a PWM pin
p.start(0)                  # Starts running PWM on the pin and sets it to 0

overall_state = {"state":2,"tail_moves": False, "last_pet":time.time(),"last_tail_moved": time.time(), "touchstatus":False, "tail_alternate": False, "motor": p,"music_busy":False,"music_writing":None}

def handle_barks(state):
    print("here")
    global overall_state
    overall_state["music_writing"] = state
    get_sound.get_new_sound(state)
    overall_state["music_writing"] = None
    print("Sound for state"+state+" updated.")

def bark():
    global overall_state
    if overall_state["music_writing"] is not overall_state["state"]:
    # if overall_state["music_writing"] is None:
        overall_state["music_busy"] = not overall_state["music_busy"]
        current_state = overall_state["state"]
        pygame.mixer.init()
        title = "/home/pi/Documents/TherapyPetRobot/thesis/sounds/new/sound_"+str(overall_state["state"])+".wav"
        pygame.mixer.music.load(title)  
        new_barks_thread = threading.Thread(target=handle_barks,args=(current_state,))
        new_barks_thread.start()
        pygame.mixer.music.play()
        pygame.mixer.music.fadeout(1000)
        # while pygame.mixer.music.get_busy:
        #     print("music busy")
        overall_state["music_busy"] = not overall_state["music_busy"]
        # new_barks_thread = threading.Thread(target=handle_barks,args=(current_state,))
        # new_barks_thread.start()

    

def handle_state():
    global overall_state
    while True:
        if time.time()-overall_state["last_pet"]>20 and overall_state["state"]>2:
            # every 20 second state drops
            overall_state["state"]-=1
            print("State dropped to "+str(overall_state["state"]))


def callback_vibration(channel):
        if GPIO.input(channel):
                print ("Movement Detected!")
        else:
                print ("Movement Detected!")
GPIO.add_event_detect(vibration_sensor, GPIO.BOTH, bouncetime=300)  # let us know when the pin 26 goes HIGH or LOW
GPIO.add_event_callback(vibration_sensor, callback_vibration)  # assign function to GPIO PIN 26, Run function on change

def distance():
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
        set_tail_angle(0 if overall_state["tail_alternate"] else 90)
        overall_state["tail_alternate"]= not overall_state["tail_alternate"]
        randtime-=1
        time.sleep(0.5)

def automatic_tail():
    global overall_state
    while True:
        if overall_state["tail_moves"]:
            time.sleep(1)
            continue
        if time.time() - overall_state["last_tail_moved"] > 7:
            print("GO CRAZY")
            move()
            time.sleep(2)
            overall_state["last_tail_moved"] = time.time()
        time.sleep(0.05)
        print("Waiting...")

def read_touchsensor():
    global overall_state, touch
    while True:
        if (GPIO.input(capacitive_touch_sensor_pin)):
            overall_state["tail_moves"] = True
            move_tail()
            overall_state["tail_moves"] = False
            overall_state["last_tail_moved"] = time.time()
        time.sleep(0.02)

def main():

    distance_thread = threading.Thread(target=distance)
    automatic_thread = threading.Thread(target=automatic_tail)
    automatic_thread.start()
    distance_thread.start()
    read_touchsensor()
    # touchsensor_thread = threading.Thread(target=read_touchsensor)
    # touchsensor_thread.start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()
    else:
        p.stop()
        GPIO.cleanup()
