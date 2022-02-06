from pathlib import Path

import cv2
from telegram import Bot


BOT_TOKEN = "5035559238:AAECCaFjCuToYx8EtTovtviFnsyvL9bo49Y"
CHAT_IDS = {
    "Manuel": "741006099",
    "Verena": "740829591",
}

bot = Bot(BOT_TOKEN)


def send_boot_up_notifications():
    for chat_id in CHAT_IDS.values():
        bot.sendMessage(chat_id, "AUTOMATED CAT FEEDER ONLINE")


def send_frame(frame, name):
    tmp_file = Path("/tmp/tmp_frame.jpg")
    cv2.imwrite(str(tmp_file), frame)
    with open(tmp_file, "rb") as file_ref:
        for chat_id in CHAT_IDS.values():
            bot.send_photo(chat_id, file_ref, caption=f"{name} is stopping by!")
    tmp_file.unlink()
