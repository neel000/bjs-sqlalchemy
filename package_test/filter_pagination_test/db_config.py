from bjs_sqlalchemy.models.config import DatabaseConfig
# DATABASE_URL = 'sqlite:///./tests/filter_pagination_test/database.db'
DATABASE_URL = "sqlite:///./filter_pagination_test/database.db"
DEBUG = False

class Session:
    def __new__(cls):
        return DatabaseConfig(db_url=DATABASE_URL)