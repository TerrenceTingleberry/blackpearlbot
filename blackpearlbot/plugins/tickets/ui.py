from os import remove, getcwd
from os.path import join as path_join
import traceback
from uuid import uuid4

from discord import (
    ButtonStyle,
    Embed,
    File,
    Interaction,
    Member,
    Message,
    SelectOption,
    TextChannel,
    utils,
)
from discord.ui import Button, Modal, TextInput, View, button, Select
from .models import PanelModel, FormModel, FieldModel

from .history_html import HTML, message


def export_html(file_name: str, messages: list[Message]) -> str:
    if not file_name.endswith(".html"):
        file_name = f"{file_name}.html"
    file_name = path_join(getcwd(), file_name)
    string = [
        message.format(
            m.created_at.strftime("%H:%M"),
            m.author,
            m.clean_content,
        )
        for m in messages
    ]
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(HTML.format("\n".join(string)))
    return file_name


class PanelEditModal(Modal, title="Edit a panel"):
    def __init__(self, panel: PanelModel):
        super().__init__(timeout=None)
        self.panel = panel
        self.add_item(
            TextInput(
                label="Panel name",
                default=panel.name,
                required=True,
            )
        )
        self.add_item(
            TextInput(
                label="Panel description",
                default=panel.description,
                required=True,
            )
        )

    async def on_submit(self, interaction: Interaction, /) -> None:
        name = self.children[0].value  # type: ignore
        description = self.children[1].value if self.children[1].value else self.panel.description  # type: ignore  # noqa: E501
        await PanelModel.update(
            self.panel.guild_id,
            self.panel.id if self.panel.id else 0,
            name=name,
            description=description,
        )
        await interaction.response.send_message(
            content="Panel updated successfully",
        )


class PanelEdit(Select):
    def __init__(self, guild_id: str, panels: list[PanelModel], **kwargs):
        self.guild_id = guild_id
        options = [SelectOption(label=p.name, value=str(p.id)) for p in panels]
        super().__init__(options=options, **kwargs)

    async def callback(self, interaction: Interaction):
        self.view.stop()  # type: ignore
        panel_id = int(self.values[0])
        panel = await PanelModel.get(self.guild_id, panel_id)
        if panel is None:
            await interaction.response.edit_message(
                content=f"Panel `{panel_id}` not found",
                view=None,
            )
            return
        modal = PanelEditModal(panel)
        await interaction.response.send_modal(modal)


class PanelDelete(Select):
    def __init__(
        self,
        guild_id: str,
        panels: list[PanelModel],
        **kwargs,
    ):
        self.guild_id = guild_id
        options = [SelectOption(label=p.name, value=str(p.id)) for p in panels]
        super().__init__(options=options, **kwargs)

    async def callback(self, interaction: Interaction):
        self.view.stop()  # type: ignore
        panel_id = int(self.values[0])
        await PanelModel.delete(guild_id=self.guild_id, panel_id=panel_id)
        await interaction.response.edit_message(
            content=f"Panel deleted successfully",
            view=None,
        )


class FieldCreate(Modal, title="Create form fields"):
    def __init__(self, form_id: int) -> None:
        super().__init__()
        self.form_id = form_id
        self.add_item(TextInput(label="Field 1", required=True))
        for i in range(1, 5):
            self.add_item(TextInput(label=f"Field {i + 1}", required=False))

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            "Form created",
            ephemeral=True,
        )
        for i in range(len(self.children)):
            if name := self.children[i].value:  # type: ignore
                await FieldModel.create(form_id=self.form_id, name=name)


class PanelSelect(Select):
    def __init__(self, options: list[SelectOption], form_inputs, **kwargs):
        super().__init__(options=options, **kwargs)
        self.form_inputs = form_inputs

    async def callback(self, interaction: Interaction):
        self.view.stop()  # type: ignore
        panel_id = self.values[0]
        form_title = self.form_inputs[0].value
        form_description = self.form_inputs[1].value
        form_id = await FormModel.create(
            panel_id=int(panel_id),  # type: ignore
            name=form_title,
            description=form_description,
        )
        await interaction.response.send_modal(
            FieldCreate(form_id=form_id),  # type: ignore
        )
        await interaction.delete_original_response()


class FormCreate(Modal, title="Create a Form"):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(TextInput(label="Form Name", required=True))
        self.add_item(TextInput(label="Form Description"))

    async def on_submit(self, interaction: Interaction) -> None:
        if not interaction.guild:
            return
        panels = await PanelModel.get_all(str(interaction.guild.id))
        if not panels:
            await interaction.response.send_message(
                "Please create a panel first",
                ephemeral=True,
            )
            return
        await interaction.response.defer()
        options = [
            SelectOption(
                label=panel.name,
                description=panel.description or "No description",
                value=panel.id,  # type: ignore
            )
            for panel in panels
        ]
        dropdown = PanelSelect(options=options, form_inputs=self.children)
        view = View()
        view.add_item(dropdown)
        await interaction.followup.send(
            "Select a panel",
            view=view,
            ephemeral=True,
        )


class FormDelete(Select):
    def __init__(self, panels: list[PanelModel], **kwargs):
        self.panels = panels
        options = []
        for panel in panels:
            for form in panel.forms:
                options.append(
                    SelectOption(
                        label=form.name,
                        value=f"{form.id}:{panel.id}",
                    )
                )
        super().__init__(options=options, **kwargs)

    async def callback(self, interaction: Interaction):
        self.view.stop()  # type: ignore
        form_id, panel_id = self.values[0].split(":")
        await interaction.response.defer()
        await FieldModel.delete_all(form_id=int(form_id))
        await FormModel.delete(form_id=int(form_id), panel_id=int(panel_id))
        await interaction.followup.send(
            "Form deleted successfully",
            ephemeral=True,
        )


class FormEdit(Modal, title="Edit form"):
    def __init__(self, form: FormModel) -> None:
        super().__init__()
        self.form = form
        self.add_item(
            TextInput(
                label="Form Name",
                default=form.name,
                required=True,
            )
        )
        self.add_item(
            TextInput(
                label="Form Description",
                default=form.description,
            )
        )

    async def on_submit(self, interaction: Interaction) -> None:
        name = self.children[0].value  # type: ignore
        description = self.children[1].value  # type: ignore
        await FormModel.update(
            panel_id=self.form.panel_id,
            form_id=self.form.id,  # type: ignore
            name=name,
            description=description or self.form.description,
        )
        await interaction.response.send_message(
            "Form edited",
            ephemeral=True,
        )


class FormSelect(Select):
    def __init__(self, panels: list[PanelModel], **kwargs):
        self.panels = panels
        options = []
        for panel in panels:
            for form in panel.forms:
                options.append(
                    SelectOption(
                        label=form.name,
                        value=f"{form.id}:{panel.id}",
                    )
                )
        super().__init__(options=options, **kwargs)

    async def callback(self, interaction: Interaction):
        self.view.stop()  # type: ignore
        form_id, panel_id = self.values[0].split(":")
        panel = next(
            (panel for panel in self.panels if panel.id == int(panel_id)),
            None,
        )
        if panel is None:
            return
        form = next(
            (form for form in panel.forms if form.id == int(form_id)),
            None,
        )

        if form is None:
            return
        await interaction.response.send_modal(FormEdit(form))
        await interaction.delete_original_response()


class PanelButton(Button):
    def __init__(self, form: FormModel, **kwargs):
        super().__init__(
            **kwargs,
        )
        self.form = form

    async def callback(self, interaction: Interaction):
        fields = await FieldModel.get_all(self.form.id)  # type: ignore
        inputs = [field.name for field in fields]
        await interaction.response.send_modal(Form(inputs))


class PanelView(View):
    def __init__(self, panel: PanelModel | None = None):
        super().__init__()
        self.value = None
        if panel is None:
            return
        for form in panel.forms:
            button = PanelButton(
                label=form.name,
                style=ButtonStyle.green,
                form=form,
            )
            self.add_item(button)


class TicketView(View):
    def __init__(self):
        super().__init__()
        self.value = None

    @button(
        label="Close Ticket",
        style=ButtonStyle.green,
        custom_id=str(uuid4()),
    )
    async def confirm(self, interaction: Interaction, button: Button):
        mention = interaction.user.mention
        self.value = f"{mention} Closed a ticket"
        #  Export chat history to a file
        if not isinstance((channel := interaction.channel), TextChannel):
            return
        messages = [
            message
            async for message in channel.history(
                limit=None,
                oldest_first=True,
            )
        ]
        file_name = "ticket"
        file_name = export_html(file_name, messages)
        if guild := interaction.guild:
            channel = utils.get(guild.channels, name="ticket-info")
            if channel is None:
                channel = await guild.create_text_channel("ticket-info")
            if not isinstance(channel, TextChannel):
                return
            await channel.send(file=File(file_name))
            await interaction.response.send_message(self.value)

            remove(file_name)
        #  Close the channel
        if isinstance(channel := interaction.channel, TextChannel):
            await channel.delete(reason="Ticket closed")


class Form(Modal, title="Ticket"):
    def __init__(self, inputs: list[str]):
        super().__init__()
        for input in inputs:
            self.add_item(TextInput(label=input, required=True))

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(
            "Thanks for your response!",
            ephemeral=True,
        )
        if guild := interaction.guild:
            channel_name = f"ticket-{uuid4().int}"
            my_channel = await guild.create_text_channel(channel_name)
            #  Add role to user and channel
            if user := interaction.user:
                if isinstance(user, Member):
                    await my_channel.set_permissions(
                        user,
                        read_messages=True,
                        send_messages=True,
                    )
                    await my_channel.set_permissions(
                        guild.default_role,
                        read_messages=False,
                        send_messages=False,
                    )
                    my_embed = Embed(
                        title="Ticket",
                        description="New support ticket",
                    )
                    for inp in self.children:
                        if isinstance(inp, TextInput):
                            my_embed.add_field(
                                name=inp.label,
                                value=inp.value,
                                inline=False,
                            )
                    my_embed.set_footer(text="Ticket created")
                    my_embed.set_author(
                        name=user.display_name,
                        icon_url=user.avatar.url
                        if user.avatar
                        else user.default_avatar.url,
                    )
                    await my_channel.send(
                        content=user.mention,
                        embed=my_embed,
                        view=TicketView(),
                    )

    async def on_error(
        self,
        interaction: Interaction,
        error: Exception,
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.",
            ephemeral=True,
        )

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)
