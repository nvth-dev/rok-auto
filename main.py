import logging
import sys

from rok_bot.bot import ROKBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    bot = ROKBot()

    if not bot.connect():
        print("Cannot connect to emulator. Check ADB is enabled.")
        print("Try: adb connect 127.0.0.1:5555")
        sys.exit(1)

    print("Connected! Starting farm barbarian...")
    print("Press Ctrl+C to stop\n")

    try:
        bot.farm_barb()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        bot.disconnect()


if __name__ == "__main__":
    main()
