from bjs_sqlalchemy import models
import unittest
import asyncio
from bjs_sqlalchemy.models import create_engine, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

class TestDatabaseConfig:
    _instance = None
    def __new__(cls, db_url, debug=False):
        if not cls._instance:
            engine = create_engine(db_url, echo=debug)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            cls._instance = Session()
        return cls._instance

class TestAsyncDatabaseConfig:
    async def __new__(cls, db_url: str, debug: bool = False):
        engine = create_async_engine(db_url, echo=debug)
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            async with session.begin():
                return session

class TestClient(unittest.TestCase):
    database_url = "sqlite:///./test.db"
    asyn_database_url = "sqlite+aiosqlite:///./test.db"
    
    @classmethod
    def setUpClass(cls):
        cls.engine = models.create_engine(cls.database_url)
        models.Base.metadata.create_all(cls.engine)
        cls.session = TestDatabaseConfig(db_url=cls.database_url)
        cls.async_session = asyncio.run(cls.__async_session())
        
    @classmethod
    async def __async_session(cls):
        return await TestAsyncDatabaseConfig(db_url=cls.asyn_database_url)

    @classmethod
    async def close_session(cls):
        await cls.async_session.close()
       
    @classmethod
    def tearDownClass(cls):
        models.Base.metadata.drop_all(cls.engine)
        cls.session.close()
        asyncio.run(cls.close_session())

    