import datetime
import time
from collections import deque

from loguru import logger

from cat import Cat
from classifier import Classifier
from feeder import Feeder, FOOD_PACKAGE_SIZE
from notifications import (
    send_boot_up_notifications,
    send_visitation_info,
    PHOTO_COOLDOWN,
)
from stream import start_stream, capture_frame

SECONDS_BETWEEN_FRAMES = 1
CONSECUTIVE_MATCHES = 4
CLASSIFIER_THRESHOLD = 0.8  # in [0., 1.]

VALIDATION_COOLDOWN = 10  # seconds

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
        self.short_term_match_history = deque(
            [None] * CONSECUTIVE_MATCHES, maxlen=CONSECUTIVE_MATCHES
        )
        self.last_photo = None

    def run(self) -> None:
        send_boot_up_notifications()
        while True:
            # effectively pause program during off hours
            if not self._is_open():
                self._closing_procedure()
                continue

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
                self._feeding_procedure(match)

            if (
                self.last_photo is None
                or (datetime.datetime.now() - self.last_photo).seconds > PHOTO_COOLDOWN
            ):
                send_visitation_info(frame, self.cats[match].name)
                self.last_photo = datetime.datetime.now()

            # control video capture cycle length
            time.sleep(
                SECONDS_BETWEEN_FRAMES
            )  # TODO: continue with while loop with condition instead

    def _is_open(self) -> bool:
        start_time, end_time = self.bank_hours
        if start_time < datetime.datetime.now().time() < end_time:
            return True
        return False

    def _feeding_procedure(self, match) -> None:
        self.feeder.dispense_food()
        time.sleep(VALIDATION_COOLDOWN)
        feeding_frame = capture_frame(self.video_stream)
        validation_match = self.classifier.validate(feeding_frame, match)
        if match != validation_match:
            logger.warning("Customer validation failed - amending error...")
            self.cats[match].amend_balance_up()
            self.cats[validation_match].amend_balance_down()

    def _closing_procedure(self) -> None:
        logger.info("Food bank is now closing for today")
        logger.info("Resetting daily food balance and sending daily reports")
        for cat in self.cats.values():
            cat.reset_balance()
            cat.send_daily_report()
        opening_time, closing_time = BANK_HOURS
        if datetime.datetime.now().time() > closing_time:
            opening_day = datetime.date.today() + datetime.timedelta(days=1)
        else:
            opening_day = datetime.date.today()
        sleep_duration = (
            datetime.datetime.combine(opening_day, opening_time)
            - datetime.datetime.now()
        )
        logger.info(
            f"Food bank opens again at {opening_time} "
            f"(in {sleep_duration.seconds / 3600:.2f} hours)"
        )
        self.video_stream.release()
        time.sleep(sleep_duration.seconds)
        logger.info("Reopening the bank now")
        self.video_stream = start_stream()

    def stop(self) -> None:
        logger.info("Gracefully stopping program")
        self.feeder.shut_down()
        self.video_stream.release()
