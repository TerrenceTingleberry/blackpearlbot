from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button

from . import models


class Confirm(View):
    def __init__(self):
        super().__init__()

    @button(label="Confirm", style=ButtonStyle.green)
    async def confirm(
        self,
        interaction: Interaction,
        button: Button,
    ):
        global CHAT_FILTERS
        if str(interaction.guild_id) in models.CHAT_FILTERS:
            models.CHAT_FILTERS.pop(str(interaction.guild_id), None)
            await models.FilterModel.delete_all(str(interaction.guild_id))
        await interaction.response.edit_message(
            content=f"Stopped all filters in {interaction.guild.name}",  # type: ignore  # noqa: E501
            view=None,
        )

    @button(label="Cancel", style=ButtonStyle.red)
    async def cancel(
        self,
        interaction: Interaction,
        button: Button,
    ):
        await interaction.response.edit_message(
            content="Cancelled",
            view=None,
        )
