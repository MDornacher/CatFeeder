import datetime
import time
from collections import deque

from loguru import logger

from cat import Cat
from classifier import Classifier
from feeder import Feeder, FOOD_PACKAGE_SIZE
from notifications import send_boot_up_notifications, send_frame
from stream import start_stream, capture_frame

NIGHT_INTERVAL = 5 * 60  # seconds
SECONDS_BETWEEN_FRAMES = 0.5
CONSECUTIVE_MATCHES = 3
PHOTO_COOLDOWN = 1 * 60  # seconds
CLASSIFIER_THRESHOLD = 0.7
BANK_HOURS = (datetime.time(9, 30), datetime.time(15, 30))


class Bank:
    def __init__(self):
        self.feeder = Feeder()
        self.classifier = Classifier()
        self.video_stream = start_stream()
        self.cats = {
            "nadir": Cat("Nadir"),
            "zenith": Cat("Zenith"),
        }

        self.bank_hours = BANK_HOURS
        self.short_term_match_history = deque([None] * CONSECUTIVE_MATCHES, maxlen=CONSECUTIVE_MATCHES)
        self.last_run = datetime.datetime.now().time()
        self.last_photo = None

    def run(self):
        send_boot_up_notifications()
        while True:
            # effectively pause program during off hours
            if not self._is_open():
                # TODO: do this with just one sleep cycle
                time.sleep(NIGHT_INTERVAL)
                continue

            # reset food balance after midnight
            if datetime.datetime.now().time() < self.last_run:
                logger.info("Resetting daily food balance")
                for cat in self.cats.values():
                    cat.reset_balance()

            # start of regular cycle
            self.last_run = datetime.datetime.now().time()

            # run classifier on frame
            frame = capture_frame(self.video_stream)
            match, certainty = self.classifier.evaluate(frame)
            logger.debug(f"Detecting {match} ({certainty})")

            if certainty > CLASSIFIER_THRESHOLD:
                self.short_term_match_history.append(match)

            # check for consecutive cat matches
            if match not in self.cats or len(set(self.short_term_match_history)) != 1:
                time.sleep(SECONDS_BETWEEN_FRAMES)
                continue

            if self.cats[match].feed(FOOD_PACKAGE_SIZE):
                self.feeder.dispense_food()
                # TODO: take some time to validate choice

            if (
                self.last_photo is None
                or (datetime.datetime.now() - self.last_photo).seconds
                > PHOTO_COOLDOWN
            ):
                send_frame(frame, self.cats[match].name)
                self.last_photo = datetime.datetime.now()

            # control video capture cycle length
            time.sleep(SECONDS_BETWEEN_FRAMES)

    def _is_open(self):
        start_time, end_time = self.bank_hours
        if start_time < datetime.datetime.now().time() < end_time:
            return True
        logger.info(
            f"Bank is currently closed and will open again at {start_time}"
        )
        return False

    def stop(self):
        logger.info("Gracefully stopping program")
        self.feeder.shut_down()
        self.video_stream.release()
        return
