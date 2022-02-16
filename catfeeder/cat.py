import datetime
from pathlib import Path

from loguru import logger

from notifications import bot, CHAT_IDS


DAILY_FOOD_BALANCE = 6  # gram
FEEDING_COOLDOWN = 90 * 60  # seconds

CAT_ACTION_LOG = Path("/home/pi/cat_actions.log")


class Cat:
    def __init__(self, name):
        self.name = name
        self.food_balance = DAILY_FOOD_BALANCE  # TODO add food consumed as property
        self.last_feeding = None
        if not CAT_ACTION_LOG.exists():
            CAT_ACTION_LOG.touch()

    def feed(self, package_size) -> bool:
        if self.last_feeding is not None:
            time_gap = datetime.datetime.now() - self.last_feeding
            if time_gap.seconds < FEEDING_COOLDOWN:
                logger.warning("Feeding cooldown is still active")
                logger.info(f"{self.name} was last fed at {self.last_feeding}")
                logger.info(
                    f"{self.name} still has to wait "
                    f"{(FEEDING_COOLDOWN - time_gap.seconds) // 60 + 1} minute(s)"
                )
                return False

        if package_size > self.food_balance:
            logger.warning(
                f"Food package with {package_size}g exceeds {self.name}'s "
                f"balance of {self.food_balance}g."
            )
            return False

        logger.info(
            f"Subtracting {package_size}g of {self.name}'s "
            f"{self.food_balance}g food balance."
        )
        self.food_balance -= package_size
        logger.debug(f"{self.food_balance}g of food balance left")
        for chat_id in CHAT_IDS.values():
            bot.sendMessage(
                chat_id,
                f"{self.name} is collecting {package_size}g of food "
                f"({DAILY_FOOD_BALANCE - self.food_balance}g total today)",
            )
        self.last_feeding = datetime.datetime.now()
        with open(CAT_ACTION_LOG, "a") as log_ref:
            log_ref.write(f"{self.last_feeding}\t{self.name}\t{package_size}\n")
        return True

    def reset_balance(self) -> None:
        logger.info(
            f"Resetting daily food balance for {self.name} ({self.food_balance}g left)"
        )
        self.food_balance = DAILY_FOOD_BALANCE

    def send_daily_report(self) -> None:
        daily_report = (
            f"{self.name.upper()}'S DAILY REPORT"
            f"\nFood consumed: {DAILY_FOOD_BALANCE - self.food_balance}g"
            f"\nLast feeding: {self.last_feeding}"
        )
        if self.food_balance > 0.0:
            daily_report += (
                f"\n\U000026A0 {self.food_balance}g food unclaimed \U000026A0"
            )
        for chat_id in CHAT_IDS.values():
            bot.sendMessage(chat_id, daily_report)
