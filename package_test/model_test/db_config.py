from bjs_sqlalchemy.models.config import DatabaseConfig as DBConfig, AsyncDatabaseConfig
DATABASE_URL = "sqlite:///./model_test/database.db"
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./model_test/database.db"
DEBUG = False

class DatabaseConfig:
    def __new__(cls):
        return DBConfig(db_url=DATABASE_URL, debug=DEBUG)

class AsyncDBSession:
    def __new__(cls):
        return AsyncDatabaseConfig(db_url=ASYNC_DATABASE_URL, debug=DEBUG)