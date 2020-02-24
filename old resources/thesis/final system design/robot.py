import RPi.GPIO as GPIO
import pygame
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random

class Robot :
    capacitive_touch_sensor_pin = 14
    servo_motor_pin = 15
    distance_echo_pin = 20
    distance_trigger_pin = 16
    vibration_sensor = 21
    overall_state = {
        "state":5,
        "tail_moves": False, 
        "last_pet":time.time(),
        "last_tail_moved": time.time(),
        "touchstatus":False,
        "tail_alternate": False,
        "motor": p,
        "music_busy":False,
        "music_writing":None,
        "last_bark":time.time()
        }
    def __init__(self):
        super().__init__()
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(capacitive_touch_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(servo_motor_pin,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
        GPIO.setup(distance_echo_pin,GPIO.IN)
        GPIO.setup(distance_trigger_pin,GPIO.OUT)
        GPIO.setup(vibration_sensor, GPIO.IN)
        p = GPIO.PWM(servo_motor_pin, 50)     # Sets up pin 11 as a PWM pin
        p.start(0)                  # Starts running PWM on the pin and sets it to 0
        automatic_thread = threading.Thread(target=self.automatic_tail)
        automatic_thread.start()
        bark_thread = threading.Thread(target=bark)
        bark_thread.start()
        self.read_touchsensor()
        try:
            # main()
            print("i am a robot")
        except KeyboardInterrupt:
            p.stop()
            GPIO.cleanup()
        else:
            p.stop()
            GPIO.cleanup()
        
        def automatic_tail(self):
            while True:
                if self.overall_state["tail_moves"]:
                    time.sleep(1)
                    continue
                if time.time() - self.overall_state["last_tail_moved"] > 15:
                    print("GO CRAZY")
                    self.move_tail()
                    time.sleep(2)
                    self.overall_state["last_tail_moved"] = time.time()
                time.sleep(0.05)
                print("Waiting...")
            
        def move_tail(self):
            randtime = random.randint(4,10)
            self.overall_state["music_busy"]=not self.overall_state["music_busy"]
            # if overall_state["music_busy"] == False:
            #     # 
            #     bark_thread.start()
            while randtime > 0:
                print(randtime)
                self.overall_state["touchstatus"] = not self.overall_state["touchstatus"]
                self.set_tail_angle(0 if self.overall_state["tail_alternate"] else 90)
                self.overall_state["tail_alternate"]= not self.overall_state["tail_alternate"]
                randtime-=1
                time.sleep(0.5)
            self.overall_state["music_busy"] = not self.overall_state["music_busy"]
        
        def set_tail_angle(self,angle):
            duty = angle / 18 + 2
            self.overall_state["motor"].ChangeDutyCycle(duty)
            sleep(0.5)
        
        def read_touchsensor(self):
            # global overall_state, touch
            while True:
                if (GPIO.input(self.capacitive_touch_sensor_pin)):
                    if self.overall_state["state"]<10:
                        self.overall_state["state"]+=1
                    self.overall_state["tail_moves"] = True
                    self.move_tail()
                    self.overall_state["tail_moves"] = False
                    self.overall_state["last_tail_moved"] = time.time()
                time.sleep(0.02)



def main():
    pet = Robot()

if __name__ == '__main__':
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     p.stop()
    #     GPIO.cleanup()
    # else:
    #     p.stop()
    #     GPIO.cleanup()