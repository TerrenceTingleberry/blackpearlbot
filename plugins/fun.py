from discord import Interaction, app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="clayton",
        description="Face Revel of Terrence",
    )
    async def clayton(self, interaction: Interaction):
        await interaction.response.send_message(
            "https://i.pinimg.com/originals/f3/25/40/f32540c61fd8c8f585bbb99161632934.jpg"  # noqa: E501
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        args = message.content.split(" ")
        if args[0] == "bruh":
            await message.channel.send(":moyai:")
        elif (
            args[0] in ("i'm", "im", "i am") and " ".join(args[1:]) == "horny"
        ):  # noqa: E501
            await message.channel.send(
                "https://tenor.com/view/vorzek-vorzneck-oglg-og-lol-gang-gif-24901093"  # noqa: E501
            )
        elif args[0] == "moo":
            await message.channel.send(
                "https://tenor.com/view/holy-cow-holy-cow-gif-25938150"
            )


async def setup(bot):  # sourcery skip: instance-method-first-arg-name
    await bot.add_cog(Fun(bot))
