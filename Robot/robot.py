import RPi.GPIO as GPIO
import pygame
import time
import os
from time import sleep   # Imports sleep (aka wait or pause) into the program
import random
import threading
import rewriteSound
import numpy as np
from sensors import Sensors
from actuators import Actuators
from audio import Audio

left_capacitive_touch_sensor_pin = 17
right_capacitive_touch_sensor_pin = 18

servo_motor_pin = 14
vibration_motor_pin = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_capacitive_touch_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_capacitive_touch_sensor_pin,
           GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Sets up pin 11 to an output (instead of an input)
GPIO.setup(servo_motor_pin, GPIO.OUT)

GPIO.setup(vibration_motor_pin, GPIO.OUT)
GPIO.output(vibration_motor_pin, GPIO.LOW)

servo_motor = GPIO.PWM(servo_motor_pin, 50)     # Sets up pin 11 as a PWM pin
# Starts running PWM on the pin and sets it to 0
servo_motor.start(0)

thread_state = {"automatic_thread": None, "state_thread": None, "bark_thread": None,
                "touch_sensor_thread": None, "vibration_thread": None, "heartbeat_audio_thread": None}


class Robot:

    def __init__(self, tail_angle, tail_alternate):
        self.state = 0
        self.tail_angle = tail_angle
        self.tail_moves = False
        self.tail_alternate = tail_alternate
        self.last_tail_moved = time.time()
        self.speaker_busy = False
        self.bark_busy = False
        self.tail_moves = False
        self.last_pet = time.time()
        self.heartbeat_busy = False
        self.main_running = True
        self.writing_sound_state = None

    def start(self):
        global thread_state
        automatic_thread = threading.Thread(target=self.automatic_tail)
        thread_state["automatic_thread"] = automatic_thread
        automatic_thread.start()

        handle_state_thread = threading.Thread(target=self.handle_state)
        thread_state["state_thread"] = handle_state_thread
        handle_state_thread .start()

        heartbeat_vibration_thread = threading.Thread(
            target=actuators.heartbeat_vibration)
        thread_state["vibration_thread"] = heartbeat_vibration_thread
        heartbeat_vibration_thread.start()

        heartbeat_audio_thread = threading.Thread(
            target=audio.make_heartbeat_sound)
        thread_state["heartbeat_audio_thread"] = heartbeat_audio_thread
        heartbeat_audio_thread.start()

        bark_audio_thread = threading.Thread(
            target=audio.bark)
        thread_state["bark_thread"] = bark_audio_thread
        bark_audio_thread.start()

    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def set_tail_angle(self, angle):
        self.tail_angle = angle

    def get_tail_angle(self):
        return self.tail_angle

    def set_tail_moves(self, value):
        self.tail_moves = True

    def get_tail_moves(self):
        return self.tail_moves

    def set_tail_alternates(self, value):
        self.tail_alternate = value

    def get_tail_alternates(self):
        return self.tail_alternate

    def set_last_tail_moved(self, value):
        self.last_tail_moved = value

    def get_last_tail_moved(self):
        return self.last_tail_moved

    def set_music_busy(self, value):
        self.speaker = False

    def get_music_busy(self, value):
        return self.speaker

    def set_bark_busy(self, value):
        self.bark_busy = False

    def get_bark_busy(self):
        return self.bark_busy

    def set_tail_moves(self, value):
        self.tail_moves = value

    def get_tail_moves(self):
        return self.tail_moves

    def set_last_pet(self, value):
        self.last_pet = value

    def get_last_pet(self):
        return self.last_pet

    def set_heartbeat_busy(self, value):
        self.heartbeat_busy = value

    def get_heartbeat_busy(self):
        return self.heartbeat_busy

    def set_writing_sound_state(self, value):
        self.writing_sound_state = value

    def get_writing_sound_state(self):
        return self.writing_sound_state

    def handle_state(self):
        while self.main_running:
            secs = random.randint(60, 200)  # 1min to 7 mins
            if time.time() - self.get_last_pet() > secs and self.get_state() > 1:
                self.set_state(self.get_state()-1)
                print("State dropped to "+str(get_state()))
                self.set_last_pet(time.time())
            time.sleep(2)

    def automatic_tail(self):
        while self.main_running:
            if self.get_tail_moves():
                time.sleep(1)
                continue
            if (time.time() - self.get_last_pet() > 120) and (self.get_bark_busy() == False and self.get_heartbeat_busy() == False):
                self.set_heartbeat_busy(False)
                self.bark_busy(False)
                time.sleep(0.5)
                bark_sound_probability = np.random.choice(
                    ["bark", "heartbeat"], p=[0.9, 0.1])
                print("Starting : "+bark_sound_probability)
                if (bark_sound_probability == "bark"):
                    self.set_heartbeat_busy(False)
                    time.sleep(0.5)
                    self.set_bark_busy(True)
                    actuators.move_tail()
                else:
                    self.set_bark_busy(False)
                    time.sleep(0.5)
                    self.set_heartbeat_busy(True)
            time.sleep(0.2)


if __name__ == '__main__':
    try:
        f = open("state.txt", "r")
        contents = f.read()
        tail_alt = contents.split("\n")[1]
        tail_angle = contents.split("\n")[2]
        robot = Robot(int(tail_angle.split(":")[1]), bool(
            tail_alt.split(":")[1]))
        actuators = Actuators(vibration_motor_pin, servo_motor, robot)
        sensors = Sensors(left_capacitive_touch_sensor_pin,
                          right_capacitive_touch_sensor_pin, robot, actuators)
        audio = Audio(robot)
        robot.start()
        read_touch_sensors_thread = threading.Thread(
            target=sensors.read_back_touch_sensors())
        thread_state["touch_sensor_thread"] = read_touch_sensors_thread
        read_touch_sensors_thread.start()

    except KeyboardInterrupt:
        f = open("state.txt", "w")
        f.write("state: "+str(robot.get_state()))
        f.write("\ntail_alternate: "+str(robot.get_tail_alternates()))
        f.write("\ntail_angle: "+str(robot.get_tail_angle()))
        f.close()
        robot.set_music_busy(False)
        robot.set_bark_busy(False)
        robot.set_heartbeat_busy(False)
        pygame.mixer.music.stop()
        robot.main_running = False
        for state in range(7):
            rewriteSound.get_new_sound(state)
        servo_motor.stop()
        GPIO.cleanup()
    else:
        servo_motor.stop()
        GPIO.cleanup()
