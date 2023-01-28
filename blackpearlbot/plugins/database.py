from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE = declarative_base()

DB_URI = getenv("DATABASE_URL", "sqlite:///database.db")


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            DB_URI,
            future=True,
            query_cache_size=1200,
        )
        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def create_all(self):
        async with self._engine.begin() as conn:  # type: ignore
            await conn.run_sync(BASE.metadata.create_all)


SESSION = AsyncDatabaseSession()
SESSION.init()
