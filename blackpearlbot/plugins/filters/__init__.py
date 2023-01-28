from .cog import Filters


async def setup(bot):
    await bot.add_cog(Filters(bot))
