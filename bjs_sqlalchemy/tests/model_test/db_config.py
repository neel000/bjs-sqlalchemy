from bjs_sqlalchemy.models import create_engine, sessionmaker

DATABASE_URL = "sqlite:///./tests/model_test/database.db"
DEBUG = False

class DatabaseConfig:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            engine = create_engine(DATABASE_URL, echo=DEBUG)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            cls._instance = Session()
        return cls._instance

def get_db():
    db = DatabaseConfig()
    try:
        yield db
    finally:
        db.close()