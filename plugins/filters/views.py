from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button

from .models import FilterModel


class Confirm(View):
    def __init__(self):
        super().__init__()

    @button(label="Confirm", style=ButtonStyle.green)
    async def confirm(
        self,
        interaction: Interaction,
        button: Button,
    ):
        await FilterModel.delete_all(
            guild_id=str(interaction.guild_id),
        )
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
