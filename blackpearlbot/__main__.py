import json
import logging
import logging.handlers
import os
import pkgutil
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from discord import Intents
from discord.ext import commands

logger = logging.getLogger(__name__)

EXCLUDE_MODULES = ["database"]


class BlackPearlBot(commands.Bot):
    def __init__(self):
        self.launch_time = datetime.utcnow()

        super().__init__(
            command_prefix="/",
            intents=Intents.all(),
            launch_time=self.launch_time,
        )

    # the method to override in order to run whatever you need
    # before your bot starts
    async def setup_hook(self):

        await self.load_extension("blackpearlbot.status")

        for p in pkgutil.iter_modules(["blackpearlbot/plugins"]):
            if p.name in EXCLUDE_MODULES:
                continue
            await self.load_extension(f"blackpearlbot.plugins.{p[1]}")


def reset_values():
    # Open the database file in read mode
    with open("database.json", "r") as f:
        # Load the contents of the file into a dictionary
        data = json.load(f)

    # Iterate through the keys in the dictionary
    for key in data.keys():
        # Set the value of each key to 0
        data[key] = 0

    # Open the file in write mode
    with open("database.json", "w") as f:
        # Write the updated dictionary to the file
        json.dump(data, f, indent=2)


scheduler = BackgroundScheduler()

# Schedule the reset_values function to run every Monday at 00:00
scheduler.add_job(reset_values, "cron", day_of_week="1", hour=0, minute=0)

scheduler.start()

if __name__ == "__main__":

    logger_discord = logging.getLogger("discord")
    logger_discord.setLevel(logging.DEBUG)
    logging.getLogger("discord.http").setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename="bot.log",
        encoding="utf-8",
        mode="a",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        dt_fmt,
        style="{",
    )
    handler.setFormatter(formatter)
    logger_discord.addHandler(handler)
    logger.addHandler(handler)

    BlackPearlBot().run(
        os.getenv(
            "TOKEN",
            "",
        )
    )
