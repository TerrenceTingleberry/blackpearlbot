import json
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from discord import Intents
from discord.ext import commands


class BlackPearlBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=Intents.all(),
        )

    # the method to override in order to run whatever you need
    # before your bot starts
    async def setup_hook(self):
        await self.load_extension("status")
        await self.load_extension("plugins.fun")
        await self.load_extension("plugins.tasks")
        await self.load_extension("plugins.tickets")
        await self.load_extension("plugins.filters")

        #  sync the commands
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} command(s)")


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

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename="bot.log",
        encoding="utf-8",
        mode="w",
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        dt_fmt,
        style="{",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    BlackPearlBot().run(
        os.getenv(
            "TOKEN",
            "",
        )
    )
