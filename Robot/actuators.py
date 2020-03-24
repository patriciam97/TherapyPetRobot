import time


class Actuators:
    def __init__(self, vibration_motor_pin, servo_motor, robot):
        self.vibration_motor_pin = vibration_motor_pin
        self.servo_motor = servo_motor
        self.robot = robot

    def set_tail_angle(self, angle):
        duty = angle / 18 + 2
        self.servo_motor.ChangeDutyCycle(duty)
        robot.set_tail_angle(angle)

    def move_tail():
        randtime = random.randint(4, 10)
        robot.set_tail_moves(True)
        print("STARTING: Tail")
        while (thread_state["main_running"] and randtime > 0):
            self.set_tail_angle(50 if robot.get_tail_alternates() else 0)
            robot.set_tail_alternates(not robot.get_tail_alternates())
            randtime -= 1
            if (robot.get_state() <= 3):
                time.sleep(0.5)
            else:
                time.sleep(0.3)
        robot.set_last_tail_moved(time.time())
        robot.set_music_busy(False)
        robot.set_bark(False)
        robot.set_tail_moves(False)
        print("STOPPING: Tail")

    def heartbeat_vibration(self):
        while self.robot.main_running:
            if robot.heartbeat_busy:
            print("STARTING:  Vibration")
            time.sleep(0.05)
            GPIO.output(vibration_motor_pin, GPIO.HIGH)
            time.sleep(0.40)
            print("STOPPING:  Vibration")
            GPIO.output(vibration_motor_pin, GPIO.LOW)
            time.sleep(0.2)
            else:
                GPIO.output(vibration_motor_pin, GPIO.LOW)
