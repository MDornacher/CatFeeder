import datetime
import time
from pathlib import Path

import cv2
import telegram
from loguru import logger

from secrets import BOT_TOKEN, CHAT_IDS  # TODO replace this with something smarter
from stream import save_frame


PHOTO_COOLDOWN = 60  # seconds
PHOTO_BURST_COOLDOWN = 3  # seconds


bot = telegram.Bot(BOT_TOKEN)


def send_message(message):
    for chat_id in CHAT_IDS.values():
        bot.sendMessage(chat_id, message)


def send_boot_up_notifications():
    logger.info("Sending out boot up notifications")
    for recipient, chat_id in CHAT_IDS.items():
        logger.debug(f"Sending notification to {recipient}")
        bot.sendMessage(chat_id, "AUTOMATED CAT FEEDER ONLINE")


def send_feeding_event(eater, food_amount, food_balance):
    message = (
        f"{eater} is collecting {food_amount}g of food "
        f"({food_balance}g food balance)",
    )
    send_message(message)


def send_frame(frame, message):
    file_path = save_frame(frame)
    with open(file_path, "rb") as file_ref:
        try:
            for recipient, chat_id in CHAT_IDS.items():
                bot.send_photo(chat_id, file_ref, caption=message)
                time.sleep(PHOTO_BURST_COOLDOWN)
        except telegram.error.BadRequest:
            logger.warning(f"Failed to send photo to {recipient}")


def send_visitation_info(frame, visitor_name):
    message = f"{visitor_name} is stopping by!"
    send_frame(frame, message)


def send_classification_error(frame, wrong_name, certainty):
    message = (
        f"\U0000274C THIEF ALERT \U0000274C"
        f"\nI'm {certainty * 100:.2} sure this is no longer {wrong_name}..."
        f"\nCorrections to the daily balance will be made \U0001F694"
    )
    send_frame(frame, message)


def send_classification_confirmation(frame, correct_name, certainty):
    message = (
        f"\U00002705 Looks good! \U00002705"
        f"\nI'm {certainty * 100:.2} sure this {correct_name}."
    )
    send_frame(frame, message)
