import json

from discord import Embed, Interaction, Member, app_commands, utils
from discord.ext import commands


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="taskdone",
        description="Adds +1 to your amount of completed tasks.",
    )
    async def taskdone(self, interaction: Interaction):
        author_id = str(interaction.user.id)
        if not isinstance(interaction.user, Member):
            return
        with open("database.json", "r") as f:
            data = json.load(f)

        if author_id in data.keys():
            data[author_id] += 1

        else:
            data[author_id] = 1

        with open("database.json", "w") as f:
            json.dump(data, f, indent=2)

        await interaction.response.send_message(
            "**Task amount updated!** :white_check_mark:"
        )

    @app_commands.command(
        name="viewtasks",
        description="Adds +1 to your amount of completed tasks.",
    )
    async def viewtasks(self, interaction: Interaction):
        if not isinstance(interaction.user, Member):
            return

        # Open the database file in read mode
        with open("database.json", "r") as database:
            # Load the contents of the file into a dictionary
            data = json.load(database)
            message_text = "".join(
                f"<@{user_id}>**: {value}**\n"
                for user_id, value in sorted(
                    data.items(), key=lambda x: x[1], reverse=True
                )
            )
            # Create the embed
            task_embed = Embed(
                title="Tasks Completed This Week",
                description=message_text,
                color=0x2F3136,
            )

            # Send the embed
            await interaction.response.send_message(embed=task_embed)


async def setup(bot):
    await bot.add_cog(Tasks(bot))
