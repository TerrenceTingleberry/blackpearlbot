from discord import Interaction, app_commands
from discord.ext import commands

from .models import FilterModel
from .views import Confirm


class Filters(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @app_commands.guild_only()
    @app_commands.command(
        name="add",
        description="Add a new filter to the server.",
    )
    async def filter(
        self,
        interaction: Interaction,
        filter: str,
        response: str,
    ):
'''
Args:
- filter: str -> name of the filter
- response: str -> the bot response triggered by the filter
'''
        await interaction.response.defer()
        cust_filter_id = await FilterModel.create(
            guild_id=str(interaction.guild_id),
            filter=filter,
            response=response,
        )
        await interaction.followup.send(f"Added filter: ``{filter}``.")
'''
Returns:
- Confirmation message and the filter name if successful
- Error if unsuccessful
'''
    @app_commands.guild_only()
    @app_commands.command(
        name="list",
        description="List all filters on the server.",
    )
    async def filters(self, interaction: Interaction):
        await interaction.response.defer()
        filters = await FilterModel.get_all(guild_id=str(interaction.guild_id))
        if not filters:
            await interaction.followup.send("No filters found")
            return
        filter_list = "\n - ".join([str(filter) for filter in filters])
        await interaction.followup.send(f"Filters:\n - {filter_list}")
'''
Returns:
- List(str) of all existing filters on the server if successful
- Message that no filters have been found if unsuccessful
'''
    @app_commands.guild_only()
    @app_commands.command(
        name="stop",
        description="Stop a filter from being used.",
    )
    async def stop(self, interaction: Interaction, filter: str):
        await interaction.response.defer()
        await FilterModel.delete(
            guild_id=str(interaction.guild_id),
            filter=filter,
        )
        await interaction.followup.send(f"Stopped filter: ``{filter}``.")
'''
Args:
- filter: str -> name of the filter

Returns:
- Stops the specified filter and sends confirmation message if successful
- Error if unsuccessful
'''
    @app_commands.guild_only()
    @app_commands.command(
        name="stopall",
        description="Stop all filters from being used.",
    )
    async def stopall(self, interaction: Interaction):
        await interaction.response.send_message(
            content="Are you sure you want to stop all filters?",
            view=Confirm(),
            ephemeral=True,
        )
'''
Returns:
- Confirmation view with buttons ['Yes', 'No'] if successful
    if 'Yes' -> stops all filters on the server
    if 'No' -> cancels the stop command
- Error if unsuccessful
'''
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
# Grabs the guild ID and only listens for filters unique to that guild
        filters = await FilterModel.get_all(guild_id=str(message.guild.id))
        for filter in filters:
            #  casefold() is used to make the string lowercase
            if filter.filter.casefold() in message.content.casefold():
                await message.reply(filter.response)
                
