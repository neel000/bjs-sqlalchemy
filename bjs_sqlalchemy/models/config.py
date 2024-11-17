from bjs_sqlalchemy.models import create_engine, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

class DatabaseConfig:
    _instance = None
    def __new__(cls, db_url, debug=False):
        if not cls._instance:
            engine = create_engine(db_url, echo=debug)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            cls._instance = Session()
        return cls._instance

# class AsyncDatabaseConfig:
#     _instance = None

#     def __new__(cls, db_url: str, debug: bool = False):
#         if not cls._instance:
#             engine = create_async_engine(db_url, echo=debug, future=True)
#             AsyncSessionLocal = sessionmaker(
#                 bind=engine,
#                 class_=AsyncSession,
#                 expire_on_commit=False,
#             )
#             cls._instance = AsyncSessionLocal

#         return cls._instance