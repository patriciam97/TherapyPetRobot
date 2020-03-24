import time
import RPi.GPIO as GPIO


class Sensors:

    def __init__(self, left_capacitive_touch_sensor_pin, right_capacitive_touch_sensor_pin, robot, actuators):
        self.left_capacitive_touch_sensor_pin = left_capacitive_touch_sensor_pin
        self.right_capacitive_touch_sensor_pin = right_capacitive_touch_sensor_pin
        self.robot = robot
        self.touch_counter = 2

    def read_back_touch_sensors(self):
        while self.robot.main_running:
            if (GPIO.input(self.right_capacitive_touch_sensor_pin) or GPIO.input(self.left_capacitive_touch_sensor_pin)) and not robot.get_bark_busy() and not robot.get_heartbeat_busy():
            print("DETECTED:  Touch sensor")
            self.set_heartbeat_busy(False)
            self.set_bark_busy(False)
            time.sleep(0.5)
            if robot.get_state() < 6 and self.touch_counter <= 0:
                print("State increased to "+str(overall_state["state"]))
                robot.set_state(robot.get_state()+1)
                self.touch_counter = random.randint(1, 3)
                 bark_sound_probability = np.random.choice(
                      ["bark", "heartbeat"], p=[0.9, 0.1])
                  print("Starting : "+bark_sound_probability)
                   if (bark_sound_probability == "bark"):
                        robot.set_heartbeat_busy(False)
                        time.sleep(0.5)
                        robot.set_bark_busy(True)
                        actuators.move_tail()
                    else:
                        robot.set_bark_busy(False)
                        time.sleep(0.5)
                        robot.set_heartbeat_busy(True)
                        actuators.make_heartbeat()
                        self.touch_counter -= 1
                    print("touch counter -1: " +
                          str(self.touch_counter))
                    time.sleep(0.2)
