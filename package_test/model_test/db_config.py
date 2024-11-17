from bjs_sqlalchemy.models.config import DatabaseConfig as DBConfig
DATABASE_URL = "sqlite:///./model_test/database.db"
DEBUG = False

class DatabaseConfig:
    def __new__(cls):
        return DBConfig(db_url=DATABASE_URL, debug=DEBUG)