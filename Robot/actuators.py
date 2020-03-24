import time
import RPi.GPIO as GPIO
import random 

class Actuators:
    def __init__(self, vibration_motor_pin, servo_motor, robot):
        self.vibration_motor_pin = vibration_motor_pin
        self.servo_motor = servo_motor
        self.robot = robot

    def set_tail_angle(self, angle):
        duty = angle / 18 + 2
        self.servo_motor.ChangeDutyCycle(duty)
        self.robot.set_tail_angle(angle)

    def move_tail(self):
        randtime = random.randint(4, 10)
        self.robot.set_tail_moves(True)
        print("STARTING: Tail")
        while (self.robot.main_running and randtime > 0):
            self.set_tail_angle(50 if self.robot.get_tail_alternates() else 0)
            self.robot.set_tail_alternates(not self.robot.get_tail_alternates())
            randtime -= 1
            if (self.robot.get_state() <= 3):
                time.sleep(0.5)
            else:
                time.sleep(0.5)
        self.robot.set_last_tail_moved(time.time())
        self.robot.set_music_busy(False)
        self.robot.set_bark_busy(False)
        self.robot.set_tail_moves(False)
        print("STOPPING: Tail")

    def heartbeat_vibration(self):
        while self.robot.main_running:
            if self.robot.heartbeat_busy:
                # print("STARTING:  Vibration")
                time.sleep(0.05)
                GPIO.output(self.vibration_motor_pin, GPIO.HIGH)
                time.sleep(0.40)
                # print("STOPPING:  Vibration")
                GPIO.output(self.vibration_motor_pin, GPIO.LOW)
                time.sleep(0.2)
            else:
                GPIO.output(self.vibration_motor_pin, GPIO.LOW)
