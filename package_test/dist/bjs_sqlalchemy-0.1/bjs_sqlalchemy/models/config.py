from bjs_sqlalchemy.models import create_engine, sessionmaker

class DatabaseConfig:
    _instance = None
    def __new__(cls, db_url, debug=False):
        if not cls._instance:
            engine = create_engine(db_url, echo=debug)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            cls._instance = Session()
        return cls._instance

