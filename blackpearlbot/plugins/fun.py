import logging

from discord import Interaction, app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        logger.info(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        logger.info(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="clayton",
        description="Face Revel of Terrence",
    )
    async def clayton(self, interaction: Interaction):
        await interaction.response.send_message(
            "https://i.pinimg.com/originals/f3/25/40/f32540c61fd8c8f585bbb99161632934.jpg"  # noqa: E501
        )


async def setup(bot):  # sourcery skip: instance-method-first-arg-name
    await bot.add_cog(Fun(bot))
