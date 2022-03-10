import time

import numpy as np
import telegram
from loguru import logger

from secrets import BOT_TOKEN, CHAT_IDS  # TODO replace this with something smarter
from stream import save_frame


PHOTO_COOLDOWN = 60  # seconds
PHOTO_BURST_COOLDOWN = 3  # seconds


bot = telegram.Bot(BOT_TOKEN)


def send_message(message: str):
    for recipient, chat_id in CHAT_IDS.items():
        logger.debug(f"Sending notification to {recipient}")
        bot.sendMessage(chat_id, message)


def send_boot_up_notifications():
    logger.info("Sending out boot up notifications")
    message = "AUTOMATED CAT FEEDER ONLINE"
    send_message(message)


def send_feeding_event(eater: str, food_amount: int, food_balance: int):
    message = (
        f"{eater} is collecting {food_amount}g of food "
        f"({food_balance}g food balance)"
    )
    send_message(message)


def send_frame(frame: np.ndarray, message: str):
    file_path = save_frame(frame)
    with open(file_path, "rb") as file_ref:
        try:
            for recipient, chat_id in CHAT_IDS.items():
                bot.send_photo(chat_id, file_ref, caption=message)
                time.sleep(PHOTO_BURST_COOLDOWN)
        except telegram.error.BadRequest:
            logger.warning(f"Failed to send photo to {recipient}")


def send_visitation_info(frame: np.ndarray, visitor_name: str):
    message = f"{visitor_name} is stopping by!"
    send_frame(frame, message)


def send_classification_error(frame: np.ndarray, wrong_name: str, certainty: float):
    message = (
        f"\U0000274C THIEF ALERT \U0000274C"
        f"\nI'm {certainty * 100:.2} sure this is no longer {wrong_name}..."
        f"\nCorrections to the daily balance will be made \U0001F694"
    )
    send_frame(frame, message)


def send_classification_confirmation(
    frame: np.ndarray, correct_name: str, certainty: float
):
    message = (
        f"\U00002705 Looks good! \U00002705"
        f"\nI'm {certainty * 100:.2} sure this {correct_name}."
    )
    send_frame(frame, message)
