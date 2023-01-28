from .cog import Tickets


async def setup(bot):
    await bot.add_cog(Tickets(bot))
