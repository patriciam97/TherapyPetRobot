import RPi.GPIO as GPIO
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading

touch = 2
motor = 3
distance_echo = 14
distance_trigger = 15
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(motor,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setup(distance_echo,GPIO.IN)
GPIO.setup(distance_trigger,GPIO.OUT)
p = GPIO.PWM(motor, 50)     # Sets up pin 11 as a PWM pin
p.start(0)                  # Starts running PWM on the pin and sets it to 0

overall_state = {"sensor_moved": False, "last_moved": time.time(), "touchstatus":False, "alternate": False, "motor": p}

def distance():
    GPIO.output(distance_trigger,True)
    time.sleep(0.0000001)
    GPIO.output(distance_trigger,False)
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(distance_echo) == 0:
        start_time = time.time()
    while GPIO.input(distance_echo) == 1:
        stop_time = time.time()
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300)/2
    return distance

def setAngle(angle):
    global overall_state
    duty = angle / 18 + 2
    overall_state["motor"].ChangeDutyCycle(duty)
    sleep(0.5)

def move():
    global overall_state
    randtime = random.randint(4,10)
    while randtime > 0:
        print(randtime)
        overall_state["touchstatus"] = not overall_state["touchstatus"]
        # if touchstatus:
        #     print("on")
        #     setAngle(30)
        # else:
        #     print("off")
        setAngle(0 if overall_state["alternate"] else 80)
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
            move()
            time.sleep(2)
            overall_state["last_moved"] = time.time()
        time.sleep(0.05)
        print("Waiting...")

def read_touchsensor():
    global alternate, overall_state, touch
    while True:
        if (GPIO.input(touch)):
            overall_state["sensor_moved"] = True
            move()
            overall_state["sensor_moved"] = False
            overall_state["last_moved"] = time.time()
        time.sleep(0.02)

def main():
    while True:
        print(distance())
    # automatic_thread = threading.Thread(target=automatic)
    # automatic_thread.start()
    # read_touchsensor()
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
