import logging
import re

from discord import Interaction, Message, app_commands
from discord.ext import commands

from . import models
from .views import Confirm

logger = logging.getLogger(__name__)


class Filters(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        logger.info(f"Loading all {self.__class__.__name__} ...")
        temp_filters = await models.FilterModel.get_all("all")

        for chat_filter in temp_filters:
            models.CHAT_FILTERS[
                chat_filter.guild_id
            ] = models.CHAT_FILTERS.get(  # get the filters for the guild
                chat_filter.guild_id, []
            )
            if chat_filter not in models.CHAT_FILTERS[chat_filter.guild_id]:
                models.CHAT_FILTERS[chat_filter.guild_id].append(chat_filter)
        logger.info(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        logger.info(f"{self.__class__.__name__} unloaded!")

    @app_commands.guild_only()
    @app_commands.command(
        name="add",
        description="Add a filter to the server",
    )
    async def add_filter(
        self,
        interaction: Interaction,
        filter: str,
        response: str,
    ):
        if interaction.guild_id is None:
            return
        await interaction.response.defer()
        guild_id = str(interaction.guild_id)
        cust_filter_id = await models.FilterModel.create(
            guild_id=str(interaction.guild_id),
            filter=filter,
            response=response,
        )

        models.CHAT_FILTERS[guild_id] = models.CHAT_FILTERS.get(guild_id, [])
        if cust_filter_id not in [
            filter.id for filter in models.CHAT_FILTERS[guild_id]
        ]:  # check if filter exists or not
            models.CHAT_FILTERS[guild_id].append(
                models.FilterModel(
                    id=cust_filter_id,
                    guild_id=guild_id,
                    filter=filter,
                    response=response,
                )
            )
        models.CHAT_FILTERS[guild_id].append(
            models.FilterModel(
                id=cust_filter_id,
                guild_id=guild_id,
                filter=filter,
                response=response,
            )
        )
        await interaction.followup.send(f"Added filter {filter}")

    @app_commands.guild_only()
    @app_commands.command(
        name="list",
        description="List all filters on the server",
    )
    async def list_filters(self, interaction: Interaction):
        if interaction.guild_id is None:
            return

        filters = models.CHAT_FILTERS.get(str(interaction.guild_id), [])
        if not filters:
            return await interaction.response.send_message(
                content="There are no filters on this server!",
            )
        filter_list = "\n - ".join([str(filter) for filter in filters])
        await interaction.response.send_message(
            content=f"Filters on this server:\n - {filter_list}"
        )

    @app_commands.guild_only()
    @app_commands.command(
        name="stop",
        description="Stop a filter from being used",
    )
    async def stop_filter(self, interaction: Interaction, filter: str):
        if interaction.guild_id is None:
            return
        await interaction.response.defer()

        if filter not in [
            filter.filter
            for filter in models.CHAT_FILTERS.get(
                str(
                    interaction.guild_id,
                ),
                [],
            )
        ]:
            return await interaction.followup.send(
                "That filter doesn't exist on this server!"
            )
        await models.FilterModel.delete(
            guild_id=str(interaction.guild_id),
            filter=filter,
        )
        models.CHAT_FILTERS[str(interaction.guild_id)] = [
            filter
            for filter in models.CHAT_FILTERS.get(
                str(interaction.guild_id),
                [],
            )
            if filter.filter != filter
        ]

        await interaction.followup.send(f"Stopped filter {filter}")

    @app_commands.guild_only()
    @app_commands.command(
        name="stopall",
        description="Stop all filters from being used",
    )
    async def filters_stopall(self, interaction: Interaction):
        if interaction.guild_id is None:
            return

        await interaction.response.send_message(
            content="Are you sure you want to stop all filters?",
            view=Confirm(),
            ephemeral=True,
        )

    @commands.Cog.listener()
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def on_message(self, message: Message):
        if message.author.bot or message.guild is None:
            return
        guild_id = str(message.guild.id)

        filters = models.CHAT_FILTERS.get(guild_id, [])
        for filter in filters:
            pattern = rf"( |^|[^\w]){re.escape(filter.filter)}( |$|[^\w])"
            if re.search(pattern, message.content, re.IGNORECASE):
                await message.reply(filter.response)
