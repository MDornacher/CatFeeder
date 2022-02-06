import datetime

from loguru import logger

from notifications import bot, CHAT_IDS

DAILY_FOOD_BALANCE = 6  # gram
FEEDING_COOLDOWN = 30 * 60  # seconds


class Cat:
    def __init__(self, name):
        self.name = name
        self.food_balance = DAILY_FOOD_BALANCE
        self.last_feeding = None

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
        for chat_id in CHAT_IDS.values():
            bot.sendMessage(chat_id, f"{self.name} is collecting {package_size}g of food")

        self.food_balance -= package_size
        logger.debug(f"{self.food_balance}g of food balance left")
        self.last_feeding = datetime.datetime.now()
        return True

    def reset_balance(self) -> None:
        logger.info(f"Resetting daily food balance for {self.name} ({self.food_balance}g left)")
        self.food_balance = DAILY_FOOD_BALANCE
