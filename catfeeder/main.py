import datetime
import time

import cv2
from loguru import logger

from cat import Cat
from classifier import initiate_model, evaluate_image
from feeder import Feeder, FOOD_PACKAGE_SIZE
from notifications import send_boot_up_notifications, send_frame


SECONDS_BETWEEN_FRAMES = 1
CONSECUTIVE_MATCHES = 10
PHOTO_COOLDOWN = 1 * 60  # seconds
CLASSIFIER_THRESHOLD = 0.6


def _main():
    send_boot_up_notifications()
    feeder = Feeder()
    cats = {
        "nadir": Cat("Nadir"),
        "zenith": Cat("Zenith"),
    }
    interpreter, input_details, output_details = initiate_model()
    video_stream = cv2.VideoCapture(0)

    short_term_match_history = [None] * CONSECUTIVE_MATCHES

    last_run = datetime.datetime.now().time()
    last_photo = None

    while True:
        try:
            ret, frame = video_stream.read()

            # validate capture / stream
            if not ret:
                logger.warning("Failed to capture image. Restarting video feed...")
                video_stream.release()
                video_stream = cv2.VideoCapture(0)
                time.sleep(5)
                continue

            # run classifier on frame
            match, certainty = evaluate_image(
                frame, interpreter, input_details, output_details
            )
            logger.debug(f"Detecting {match} ({certainty})")

            if certainty > CLASSIFIER_THRESHOLD:
                # check match history
                short_term_match_history.append(match)
                short_term_match_history.pop(0)
                if len(short_term_match_history) != CONSECUTIVE_MATCHES:
                    logger.warning(
                        f"Short term match history is broken ({short_term_match_history}) "
                        "and will be reset"
                    )
                    short_term_match_history = [None] * CONSECUTIVE_MATCHES
                    logger.debug(
                        f"New short term match history: {short_term_match_history}"
                    )
                    continue

                # check if feeding conditions are met
                if (
                    match in cats
                    and len(set(short_term_match_history)) == 1
                    and feeder.is_open()
                ):
                    if (
                        last_photo is None
                        or (datetime.datetime.now() - last_photo).seconds
                        > PHOTO_COOLDOWN
                    ):
                        send_frame(frame, match)
                        last_photo = datetime.datetime.now()
                    if cats[match].feed(FOOD_PACKAGE_SIZE):
                        feeder.dispense_food()

            # reset food balance after midnight
            if datetime.datetime.now().time() < last_run:
                logger.info("Resetting daily food balance")
                for cat in cats.values():
                    cat.reset_balance()

            # control video capture cycle length
            time.sleep(SECONDS_BETWEEN_FRAMES)

            last_run = datetime.datetime.now().time()

        except KeyboardInterrupt:
            logger.info("Gracefully stopping program")
            feeder.shut_down()
            video_stream.release()
            return


if __name__ == "__main__":
    _main()
