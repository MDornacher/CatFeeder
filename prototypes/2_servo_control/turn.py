from gpiozero import Servo
from time import sleep


servo = Servo(17)

while True:
    servo.min()
    print("min", end="\r")
    sleep(1)
    servo.mid()
    print("mid", end="\r")
    sleep(1)
    servo.max()
    print("max", end="\r")
    sleep(1)
    servo.mid()
    print("mid", end="\r")
    sleep(1)

