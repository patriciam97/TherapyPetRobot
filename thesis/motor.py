# Set up libraries and overall settings
import RPi.GPIO as GPIO  # Imports the standard Raspberry Pi GPIO library
from time import sleep   # Imports sleep (aka wait or pause) into the program
import cv2 as cv
import asyncio

GPIO.setmode(GPIO.BOARD) # Sets the pin numbering system to use the physical layout

# initilize
GPIO.setup(11,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
GPIO.setwarnings(False)
p = GPIO.PWM(11, 50)     # Sets up pin 11 as a PWM pin
p.start(0)               # Starts running PWM on the pin and sets it to 0

cap = cv.VideoCapture(0)
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

# while True:
# 	print("next")
# 	p.ChangeDutyCycle(3)     # Changes the pulse width to 3 (so moves the servo)
# 	# sleep(1)   
# 	ret, frame = cap.read()
# 	gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
# 	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
# 	if (len(faces) == 1 ):
# 		break
# 	# if cv2.waitKey(1) & 0xFF == ord('q'):
#     #     break

# cap.release()
# cv.destroyAllWindows()
# p.stop()                 # At the end of the program, stop the PWM
# GPIO.cleanup()           # Resets the GPIO pins back to defaults
async def main():
    print("heyyyy")
    print("heyyyy2")
    print("heyyyy3")
    await asyncio.sleep(2) #delayes
    print("heyyyy4")

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print('done')