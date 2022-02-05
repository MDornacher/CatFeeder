import time

import RPi.GPIO as GPIO
from loguru import logger

RELAY_PIN = 2
SWITCH_PIN = 27

CYCLE_COOLDOWN = 0.5  # seconds
SWITCH_COOLDOWN = 0.05  # seconds


def setup() -> None:
    logger.info("Setup GPIO")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.HIGH)


def teardown() -> None:
    logger.info("Teardown GPIO")
    GPIO.cleanup()


def start_motor() -> None:
    logger.debug("Starting motor")
    GPIO.output(RELAY_PIN, GPIO.LOW)


def stop_motor() -> None:
    logger.debug("Stopping motor")
    GPIO.output(RELAY_PIN, GPIO.HIGH)


def check_switch() -> bool:
    if GPIO.input(SWITCH_PIN):
        logger.trace("Switch is pressed")
        return True
    logger.trace("Switch is open")
    return False


def reset() -> None:
    start_motor()
    while not check_switch():
        logger.trace("Waiting for switch to be pressed")
        time.sleep(SWITCH_COOLDOWN)
    stop_motor()
    logger.info("Mechanics have been reset")


def cycle() -> None:
    logger.debug("Starting cycle")
    start_motor()
    time.sleep(CYCLE_COOLDOWN)
    while not check_switch():
        logger.trace("Waiting for switch to be pressed")
        time.sleep(SWITCH_COOLDOWN)
    stop_motor()
    logger.info("Cycle has been completed")
