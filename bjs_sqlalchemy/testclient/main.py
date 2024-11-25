from bjs_sqlalchemy import models
from bjs_sqlalchemy.models.config import DatabaseConfig, AsyncDatabaseConfig
import unittest
import asyncio

class TestClient(unittest.TestCase):
    database_url = "sqlite:///./test.db"
    asyn_database_url = "sqlite+aiosqlite:///./test.db"
    
    @classmethod
    def setUpClass(cls):
        cls.engine = models.create_engine(cls.database_url)
        models.Base.metadata.create_all(cls.engine)
        cls.session = DatabaseConfig(db_url=cls.database_url)
        cls.async_session = asyncio.run(cls.__async_session())
        
    @classmethod
    async def __async_session(cls):
        return await AsyncDatabaseConfig(db_url=cls.asyn_database_url)

    @classmethod
    async def close_session(cls):
        await cls.async_session.close()
       
    @classmethod
    def tearDownClass(cls):
        models.Base.metadata.drop_all(cls.engine)
        cls.session.close()
        asyncio.run(cls.close_session())

    