from sqlalchemy import Column, Integer
from .mixin import CreateMixin, UpdateMixin, DeleteMixin
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base()

class Model(Base, CreateMixin, UpdateMixin, DeleteMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)

    async def save(self, session, refresh=True):
        return await self.create(
            session, refresh=refresh
        ) if not self.id else await self.update(
            session, refresh=refresh
        )

