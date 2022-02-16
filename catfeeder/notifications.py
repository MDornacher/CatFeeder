import datetime
import time
from pathlib import Path

import cv2
import telegram
from loguru import logger

from secrets import BOT_TOKEN, CHAT_IDS  # TODO replace this with something smarter


bot = telegram.Bot(BOT_TOKEN)


def send_boot_up_notifications():
    logger.info("Sending out boot up notifications")
    for recipient, chat_id in CHAT_IDS.items():
        logger.debug(f"Sending notification to {recipient}")
        bot.sendMessage(chat_id, "AUTOMATED CAT FEEDER ONLINE")


def send_frame(frame, name):
    file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    file_path = Path(f"/home/pi/Pictures/{file_name}")
    cv2.imwrite(str(file_path), frame)
    with open(file_path, "rb") as file_ref:
        try:
            for recipient, chat_id in CHAT_IDS.items():
                bot.send_photo(chat_id, file_ref, caption=f"{name} is stopping by!")
                time.sleep(3)
        except telegram.error.BadRequest:
            logger.warning(f"Failed to send photo to {recipient}")
