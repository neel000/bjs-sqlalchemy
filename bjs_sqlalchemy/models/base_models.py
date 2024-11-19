from sqlalchemy import Column, Integer
from .mixin import CreateMixin, UpdateMixin, DeleteMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base()

class Model(Base, CreateMixin, UpdateMixin, DeleteMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)

    def save(self, session, refresh=True):
        return self.create(
            session, refresh=refresh
        ) if not self.id else self.update(
            session, refresh=refresh
        )

    async def async_save(self, session, refresh=True):
        return await self._async_create(
            session, refresh=refresh
        ) if not self.id else await self._async_update(
            session, refresh=refresh
        )

