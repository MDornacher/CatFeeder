from bank import Bank


if __name__ == "__main__":
    bank = Bank()
    try:
        bank.run()
    except KeyboardInterrupt:
        bank.stop()
