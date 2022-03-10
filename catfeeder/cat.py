import datetime
from pathlib import Path
from collections import deque
from typing import Optional

from loguru import logger

from notifications import send_feeding_event, send_message


DAILY_FOOD_BALANCE = 6  # gram
FEEDING_COOLDOWN = 90 * 60  # seconds
FEEDING_HISTORY_SIZE = 3

CAT_ACTION_LOG = Path("/home/pi/cat_actions.log")


class Cat:
    def __init__(self, name):
        self.name = name
        self.food_balance = DAILY_FOOD_BALANCE
        self.last_feedings = deque(
            [None] * FEEDING_HISTORY_SIZE, maxlen=FEEDING_HISTORY_SIZE
        )
        if not CAT_ACTION_LOG.exists():
            CAT_ACTION_LOG.touch()

    @property
    def last_feeding(self) -> Optional[datetime.datetime]:
        return self.last_feedings[-1]

    @property
    def food_consumed(self) -> int:
        return DAILY_FOOD_BALANCE - self.food_balance

    def feed(self, package_size) -> bool:
        """
        Decide if food is allowed to be offered based on multiple conditions,
        while keeping track of feeding events.
        """
        # active feeding cooldown?
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

        # exceeding food balance?
        if package_size > self.food_balance:
            logger.warning(
                f"Food package with {package_size}g exceeds {self.name}'s "
                f"balance of {self.food_balance}g."
            )
            return False

        # all pre-checks cleared => booking feeding event
        self.change_balance(-package_size)
        self.last_feedings.append(datetime.datetime.now())
        logger.debug(f"{self.food_balance}g of food balance left")
        send_feeding_event(self.name, package_size, self.food_balance)
        return True

    def amend_balance_up(self, package_size) -> None:
        """
        Correct for incorrectly subtracted food disposal.
        """
        logger.info(f"Amending food balance for {self.name} by {package_size} up.")
        self.change_balance(+package_size)
        self.last_feedings.appendleft(None)

    def amend_balance_down(self, package_size) -> None:
        """
        Correct for food theft / false match.
        """
        logger.info(f"Amending food balance for {self.name} by {package_size} down.")
        self.change_balance(-package_size)
        self.last_feedings.append(datetime.datetime.now())

    def change_balance(self, package_size) -> None:
        """
        Wrap food balance change with different log events
        """
        logger.info(
            f"Changing {self.name}'s food balance "
            f"of {self.food_balance}g by {package_size}g"
        )
        self.food_balance += package_size
        with open(CAT_ACTION_LOG, "a") as log_ref:
            log_ref.write(f"{self.last_feeding}\t{self.name}\t{package_size}\n")

    def reset_balance(self) -> None:
        logger.info(
            f"Resetting daily food balance for {self.name} ({self.food_balance}g left)"
        )
        self.food_balance = DAILY_FOOD_BALANCE

    def send_daily_report(self) -> None:
        daily_report = (
            f"{self.name.upper()}'S DAILY REPORT"
            f"\nFood consumed: {self.food_consumed}g"
            f"\nLast feeding: {self.last_feeding}"
        )
        if self.food_balance > 0.0:
            daily_report += (
                f"\n\U000026A0 {self.food_balance}g food unclaimed \U000026A0"
            )
        if self.food_balance < 0.0:
            daily_report += (
                f"\n\U000026A0 {abs(self.food_balance)} food overclaimed \U000026A0"
            )
        send_message(daily_report)
