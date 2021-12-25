import RPi.GPIO as io
import time


LED_GPIO = 27

io.setmode(io.BCM)
io.setup(LED_GPIO, io.OUT)

while True:
    io.output(LED_GPIO, True)
    print("ON ", end="\r")
    time.sleep(1)
    io.output(LED_GPIO, False)
    print("OFF", end="\r")
    time.sleep(1)
