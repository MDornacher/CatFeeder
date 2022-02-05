import time

from loguru import logger

from feeder import Feeder, FOOD_PACKAGE_SIZE
from cat import Cat


def _main():
    feeder = Feeder()
    nadir = Cat("Nadir")
    zenith = Cat("Zenith")

    """
    add camera interaction
    &
    some ML magic
    """


def _test():
    feeder = Feeder()
    nadir = Cat("Nadir")

    time.sleep(5)
    while True:
        try:
            logger.info("Nadir detected!")
            if feeder.is_open() and nadir.feed(FOOD_PACKAGE_SIZE):
                feeder.dispense_food()

            logger.info("Continue simulation in 30 seconds")
            time.sleep(30)
        except KeyboardInterrupt:
            print("Stopped")
            feeder.shut_down()
            return


if __name__ == "__main__":
    # _main()
    _test()
