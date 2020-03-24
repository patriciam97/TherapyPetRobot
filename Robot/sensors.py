import time
import RPi.GPIO as GPIO
import random
import numpy as np

class Sensors:

    def __init__(self, left_capacitive_touch_sensor_pin, right_capacitive_touch_sensor_pin, robot, actuators):
        self.left_capacitive_touch_sensor_pin = left_capacitive_touch_sensor_pin
        self.right_capacitive_touch_sensor_pin = right_capacitive_touch_sensor_pin
        self.robot = robot
        self.touch_counter = 2
        self.actuators = actuators

    def read_back_touch_sensors(self):
        while self.robot.main_running:
            if (GPIO.input(self.right_capacitive_touch_sensor_pin) or GPIO.input(self.left_capacitive_touch_sensor_pin)) and ((time.time()-self.robot.get_last_pet())>=5)  and not self.robot.get_bark_busy() and not self.robot.get_heartbeat_busy():
                print("DETECTED:  Touch sensor")
                print("TOUCH COUNTER VALUE: "+ str(self.touch_counter))
                self.robot.set_heartbeat_busy(False)
                self.robot.set_bark_busy(False)
                time.sleep(0.5)
                self.touch_counter-=1
                if self.robot.get_state() < 6 and self.touch_counter <= 0:
                    print("INCREASING STATE "+str(self.robot.get_state()))
                    self.robot.set_state(self.robot.get_state()+1)
                    self.touch_counter = random.randint(1, 3)
                    self.robot.set_bark_busy(True)
                    bark_sound_probability = np.random.choice(
                        ["bark", "heartbeat"], p=[0.9, 0.1])
                    print("STARTING : "+bark_sound_probability)
                    self.robot.set_last_pet(time.time())
                    if (bark_sound_probability == "bark"):
                        self.robot.set_heartbeat_busy(False)
                        time.sleep(0.5)
                        self.robot.set_bark_busy(True)
                        self.actuators.move_tail()
                    else:
                        self.robot.set_bark_busy(False)
                        time.sleep(0.5)
                        self.robot.set_heartbeat_busy(True)
                        self.actuators.heartbeat_vibration()
                        self.touch_counter -= 1
                        print("touch counter -1: " +
                            str(self.touch_counter))
                        time.sleep(0.2)
