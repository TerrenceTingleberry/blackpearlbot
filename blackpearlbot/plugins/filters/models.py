from typing import Optional

from sqlalchemy import delete, select, update

from blackpearlbot.plugins.database import SESSION

from .database import Filter


class FilterModel:
    def __init__(
        self,
        id: int,
        guild_id: str,
        filter: str,
        response: str,
        **kwargs,
    ):
        self.id = id
        self.guild_id = guild_id
        self.filter = filter
        self.response = response

    def __repr__(self):
        return "<Filter %r in %r>" % (self.filter, self.guild_id)

    def __str__(self):
        return self.filter

    def __dict__(self):
        return {
            "id": self.id,
            "guild_id": self.guild_id,
            "filter": self.filter,
            "response": self.response,
        }

    @classmethod
    async def create(
        cls,
        guild_id: str,
        filter: str,
        response: str,
        **kwargs,
    ) -> int:  # sourcery skip: avoid-builtin-shadow
        #  check if filter exists:
        _filter = filter.casefold()
        query = select(Filter).where(
            Filter.filter == _filter,
            Filter.guild_id == guild_id,
        )
        cust_filter = await SESSION.execute(query)
        if cust_filter := cust_filter.scalars().first():
            await cls.update(
                guild_id=guild_id,
                filter=filter,
                new_response=response,
            )
            return cust_filter.id  # type: ignore
        cust_filter = Filter(
            guild_id=guild_id,
            filter=filter,
            response=response,
        )
        SESSION.add(cust_filter)
        try:
            await SESSION.commit()
            return cust_filter.id  # type: ignore
        except Exception as e:
            await SESSION.rollback()
            raise e

    @classmethod
    async def get(cls, guild_id: str, id: int) -> Optional["FilterModel"]:
        query = select(Filter).where(
            Filter.id == id,
            Filter.guild_id == guild_id,
        )
        cust_filter = await SESSION.execute(query)
        if cust_filter := cust_filter.scalars().first():
            return cls(**cust_filter.__dict__)
        return None

    @classmethod
    async def get_all(cls, guild_id: str = "all") -> list["FilterModel"]:
        if guild_id == "all":
            query = select(Filter)
        else:
            query = select(Filter).where(Filter.guild_id == guild_id)
        cust_filters = await SESSION.execute(query)
        return (
            [
                cls(**cust_filter.__dict__)
                for cust_filter in cust_filters.scalars().all()
            ]
            if cust_filters
            else []
        )

    @classmethod
    async def delete(cls, guild_id: str, filter: str) -> None:
        # sourcery skip: avoid-builtin-shadow
        _filter = filter.casefold()
        query = delete(Filter).where(
            Filter.filter == _filter,
            Filter.guild_id == guild_id,
        )
        await SESSION.execute(query)

        try:
            await SESSION.commit()
        except Exception as e:
            await SESSION.rollback()
            raise e

    @classmethod
    async def update(
        cls,
        guild_id: str,
        filter: str,
        new_response: str,
    ) -> None:
        _filter = filter.casefold()
        query = (
            update(Filter)
            .where(
                Filter.filter == _filter,
                Filter.guild_id == guild_id,
            )
            .values(response=new_response)
        )
        await SESSION.execute(query)

        try:
            await SESSION.commit()
        except Exception as e:
            await SESSION.rollback()
            raise e

    @classmethod
    async def delete_all(cls, guild_id: str) -> None:
        query = delete(Filter).where(Filter.guild_id == guild_id)
        await SESSION.execute(query)

        try:
            await SESSION.commit()
        except Exception as e:
            await SESSION.rollback()
            raise e


CHAT_FILTERS: dict[str, list[FilterModel]] = {}
