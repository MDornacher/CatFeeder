import datetime

from loguru import logger

import mechanics
from notifications import bot, CHAT_IDS

FOOD_PACKAGE_SIZE = 6  # gram
CYCLE_REMINDER = 10
SHOP_HOURS = (datetime.time(6), datetime.time(22))


class Feeder:
    def __init__(self):
        self.food_cycles = 0
        self.shop_hours = SHOP_HOURS

        mechanics.setup()
        mechanics.reset()
        logger.info("Feeder initiated")

    def is_open(self):
        start_time, end_time = self.shop_hours
        if start_time < datetime.datetime.now().time() < end_time:
            return True
        logger.info(
            f"Food dispenser is currently closed and will open again at {start_time}"
        )
        return False

    def dispense_food(self) -> None:
        logger.info("Dispensing food")
        mechanics.cycle()
        self.food_cycles += 1
        logger.debug(f"Number of completed food cycles: {self.food_cycles}")
        if self.food_cycles % CYCLE_REMINDER == 0:
            self.send_refill_reminder()

    def send_refill_reminder(self):
        logger.info(
            f"Sending refill reminder via Telegram to {len(CHAT_IDS)} recipients"
        )
        message = (
            "Periodic reminder to check the food level "
            f"in the cat feeder ({self.food_cycles} cycles)"
        )
        for recipient, chat_id in CHAT_IDS.items():
            logger.debug(f"Sending reminder to {recipient} ({chat_id})")
            bot.sendMessage(chat_id, message)

    def shut_down(self) -> None:
        logger.info("Shutting down feeder")
        mechanics.teardown()
