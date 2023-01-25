import json

from discord import Button, Interaction, app_commands
from discord.ext import commands

from .ui import PanelView, TicketView, FormCreate
from .models import PanelModel, FormModel, FieldModel


@app_commands.guild_only()
class Tickets(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    async def setup_hook(self):
        self.bot.add_view(PanelView())
        self.bot.add_view(TicketView())

    panel = app_commands.Group(
        name="panel",
        description="Manage ticket panels",
    )

    @panel.command(
        name="create",
        description="Create a ticket panel",
    )
    async def panel_create(
        self,
        interaction: Interaction,
        name: str,
        description: str = "",
    ):
        guild_id = interaction.guild_id or 0
        await PanelModel.create(
            guild_id=str(guild_id),
            name=name,
            description=description,
        )
        await interaction.response.send_message(
            f"Created panel `{name}`",
            ephemeral=True,
        )

    @panel.command(
        name="delete",
        description="Delete a ticket panel",
    )
    async def panel_delete(
        self,
        interaction: Interaction,
        panel_id: int,
    ):
        guild_id = interaction.guild_id or 0
        await PanelModel.delete(str(guild_id), panel_id)
        await interaction.response.send_message(
            f"Deleted panel `{panel_id}`",
            ephemeral=True,
        )

    @panel.command(
        name="list",
        description="List ticket panels",
    )
    async def panel_list(self, interaction: Interaction):
        guild_id = interaction.guild_id or 0
        panels = await PanelModel.get_all(str(guild_id))
        ret_list = []
        for panel in panels:
            panel_dict = {
                "id": panel.id,
                "name": panel.name,
                "description": panel.description,
            }
            ret_list.append(panel_dict)
        await interaction.response.send_message(
            f"Panels: ```json\n{json.dumps(ret_list, indent=4)}```",
        )

    @panel.command(
        name="edit",
        description="Edit a ticket panel",
    )
    async def panel_edit(
        self,
        interaction: Interaction,
        panel_id: int,
        name: str,
        description: str = "",
    ):
        guild_id = interaction.guild_id or 0
        await PanelModel.update(
            guild_id=str(guild_id),
            panel_id=panel_id,
            name=name,
            description=description,
        )
        await interaction.response.send_message(
            f"Edited panel `{panel_id}`",
            ephemeral=True,
        )

    @panel.command(
        name="send",
        description="Send a ticket panel",
    )
    async def panel_send(
        self,
        interaction: Interaction,
        panel_id: int,
    ):
        guild_id = interaction.guild_id or 0
        panel = await PanelModel.get(str(guild_id), panel_id)
        if not panel:
            await interaction.response.send_message(
                f"Panel `{panel_id}` not found",
                ephemeral=True,
            )
            return
        panelview = PanelView(panel)
        title = f"**{panel.name}**"
        description = panel.description
        content = f"{title}\n{description}"
        await interaction.response.send_message(
            content=content,
            view=panelview,
        )

    form = app_commands.Group(
        name="form",
        description="Manage ticket forms",
    )

    @form.command(
        name="create",
        description="Create a ticket form",
    )
    async def form_create(
        self,
        interaction: Interaction,
    ):
        await interaction.response.send_modal(FormCreate())

    @form.command(
        name="delete",
        description="Delete a ticket form",
    )
    async def form_delete(
        self,
        interaction: Interaction,
        panel_id: int,
        form_id: int,
    ):
        await FormModel.delete(panel_id, form_id)
        await interaction.response.send_message(
            f"Deleted form `{form_id}`",
            ephemeral=True,
        )

    @form.command(
        name="list",
        description="List ticket forms",
    )
    async def form_list(
        self,
        interaction: Interaction,
        panel_id: int,
    ):
        forms = await FormModel.get_all(panel_id)
        ret_list = [
            {
                "id": form.id,
                "name": form.name,
                "description": form.description,
            }
            for form in forms
        ]
        await interaction.response.send_message(
            f"Forms: ```json\n{json.dumps(ret_list, indent=4)}```"
        )

    @form.command(
        name="edit",
        description="Edit a ticket form",
    )
    async def form_edit(
        self,
        interaction: Interaction,
        panel_id: int,
        form_id: int,
        name: str,
        description: str = "",
    ):
        await FormModel.update(
            panel_id=panel_id,
            form_id=form_id,
            name=name,
            description=description,
        )
        await interaction.response.send_message(
            f"Edited form `{form_id}`",
            ephemeral=True,
        )

    field = app_commands.Group(
        name="field",
        description="Manage ticket fields",
    )

    @field.command(
        name="create",
        description="Create a ticket field",
    )
    async def field_create(
        self,
        interaction: Interaction,
        form_id: int,
        name: str,
    ):
        await FieldModel.create(
            form_id=form_id,
            name=name,
            response="",
        )
        await interaction.response.send_message(
            f"Created field `{name}`",
            ephemeral=True,
        )

    @field.command(
        name="delete",
        description="Delete a ticket field",
    )
    async def field_delete(
        self,
        interaction: Interaction,
        form_id: int,
        field_id: int,
    ):
        await FieldModel.delete(form_id, field_id)
        await interaction.response.send_message(
            f"Deleted field `{field_id}`",
            ephemeral=True,
        )

    @field.command(
        name="list",
        description="List ticket fields",
    )
    async def field_list(
        self,
        interaction: Interaction,
        form_id: int,
    ):
        fields = await FieldModel.get_all(form_id)
        fields = [field.__dict__ for field in fields]
        await interaction.response.send_message(
            f"Fields: ```json\n{json.dumps(fields, indent=4)}```",
        )

    @field.command(
        name="edit",
        description="Edit a ticket field",
    )
    async def field_edit(
        self,
        interaction: Interaction,
        form_id: int,
        field_id: int,
        name: str,
    ):
        await FieldModel.update(
            form_id=form_id,
            field_id=field_id,
            response="",
            name=name,
        )
        await interaction.response.send_message(
            f"Edited field `{field_id}`",
            ephemeral=True,
        )
