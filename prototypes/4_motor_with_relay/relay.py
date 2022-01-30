import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.HIGH)

try:
    while True:
        print("Setting to low")
        GPIO.output(2, GPIO.LOW)
        time.sleep(2)
        print("Setting to high")
        GPIO.output(2, GPIO.HIGH)
        time.sleep(1.35)
except KeyboardInterrupt:
    print("Stopped")
    GPIO.cleanup()
