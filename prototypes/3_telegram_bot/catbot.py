#!/usr/bin/python

import argparse
import datetime
from pathlib import Path

from telegram import Bot


BOT_TOKEN = "5026991960:AAE3MX1O3WbxCOQOwH7_qPF-HFWqfY2vLw4"
CHAT_ID = "741006099"

IMAGE_LIBRARY = Path("/mnt/share/")

LOCK_FILE = IMAGE_LIBRARY / "catbot.lock"
COOLDOWN_IN_SEC = 60


def read_lock_file():
    with open(LOCK_FILE) as file_ref:
        last_execution_time = datetime.datetime.fromtimestamp(float(file_ref.read()))
    return last_execution_time


def write_lock_file(now):
    with open(LOCK_FILE, "w") as file_ref:
        file_ref.write(str(now.timestamp()))


def check_cooldown():
    now = datetime.datetime.now()
    try:
        last_execution_time = read_lock_file()
    except FileNotFoundError:
        last_execution_time = now
        write_lock_file(now)

    last_run_delta = now - last_execution_time
    if last_run_delta.seconds < COOLDOWN_IN_SEC:
        print(f"Cooldown still active: {COOLDOWN_IN_SEC - last_run_delta.seconds} second(s)")
        exit()


def latest_file(path: Path, pattern: str = "*.jpg"):
    files = path.glob(pattern)
    return max(files, key=lambda x: x.stat().st_ctime)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=None)
    args = parser.parse_args()

    photo_path = args.file if args.file is None else latest_file(IMAGE_LIBRARY)

    bot = Bot(BOT_TOKEN)
    print("Sending image...")
    bot.send_photo(
        CHAT_ID,
        photo=open(photo_path, "rb"),
        caption="We have a visitor!",
    )

    now = datetime.datetime.now()
    write_lock_file(now)
