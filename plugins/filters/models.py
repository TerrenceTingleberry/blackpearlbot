from typing import Optional

from sqlalchemy import delete, select, update

from plugins.database import SESSION

from .database import Filter


class FilterModel:
'''
Args:
id: int -> id
guild_id: str -> id of the guild
filter: str -> name of the filter
response: str -> bot response to the filter
'''
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
# Find and return the fliter from the given guild
    def __repr__(self):
        return "<Filter %r in %r>" % (self.filter, self.guild_id)

    def __str__(self):
        return self.filter
# Store keys in a dictionary
    def __dict__(self):
        return {
            "id": self.id,
            "guild_id": self.guild_id,
            "filter": self.filter,
            "response": self.response,
        }

    @classmethod
'''
Args:
guild_id: str -> id of the guild
filter: str -> name of the filter
response: str -> bot response to the filter

Return:
- Id if successful
- Error if unsuccessful
'''
    async def create(
        cls,
        guild_id: str,
        filter: str,
        response: str,
        **kwargs,
    ) -> int:  # sourcery skip: avoid-builtin-shadow
        #  Check if filter exists:
        filter = filter.casefold()
        # Casefold to automatically lowercase the filter
        query = select(Filter).where(
            Filter.filter == filter,
            Filter.guild_id == guild_id,
        )
        cust_filter = await SESSION.execute(query)
        # If filter already exists, update the response
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
'''
Args:
guild_id: str -> id of the guild
id: int -> id

Return:
- Optional["FilterModel"] if successful
- None if unsuccessful
'''
    async def get(cls, guild_id: str, id: int) -> Optional["FilterModel"]:
        # Select the filter that matches filter and guild id
        query = select(Filter).where(
            Filter.id == id,
            Filter.guild_id == guild_id,
        )
        cust_filter = await SESSION.execute(query)
        if cust_filter := cust_filter.scalars().first():
            return cls(**cust_filter.__dict__)
        return None

    @classmethod
'''
Args:
guild_id: str -> id of the guild

Return:
- list["FilterModel"] if successful
- [] if unsuccessful
'''
    async def get_all(cls, guild_id: str) -> list["FilterModel"]:
        # Select all filters from a guild
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
'''
Args:
guild_id: str -> id of the guild
filter: str -> name of the filter

Return:
- None if successful
- Error if unsuccessful
'''
    async def delete(cls, guild_id: str, filter: str) -> None:
        # sourcery skip: avoid-builtin-shadow
        filter = filter.casefold()
        # Delete the specified filter from the guild
        query = delete(Filter).where(
            Filter.filter == filter,
            Filter.guild_id == guild_id,
        )
        await SESSION.execute(query)

        try:
            await SESSION.commit()
        except Exception as e:
            await SESSION.rollback()
            raise e

    @classmethod
'''
Args:
guild_id: str -> id of the guild
filter: str -> name of the filter
new_response: str -> the updated response

Return:
- None if successful
- Error if unsuccessful
'''
    async def update(
        cls,
        guild_id: str,
        filter: str,
        new_response: str,
    ) -> None:  # sourcery skip: avoid-builtin-shadow
        filter = filter.casefold()
        # Update the specified filter in the guild
        query = (
            update(Filter)
            .where(
                Filter.filter == filter,
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
'''
Args:
guild_id: str -> id of the guild

Return:
- None if successful
- Error if unsuccessful
'''
    @classmethod
    async def delete_all(cls, guild_id: str) -> None:
        # Delete all filters of a guild
        query = delete(Filter).where(Filter.guild_id == guild_id)
        await SESSION.execute(query)

        try:
            await SESSION.commit()
        except Exception as e:
            await SESSION.rollback()
            raise e
