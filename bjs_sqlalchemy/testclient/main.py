from bjs_sqlalchemy import models
from bjs_sqlalchemy.models.config import DatabaseConfig 
import unittest
import os

class TestClient(unittest.TestCase):
    database_url = "sqlite:///./test.db"
    
    @property
    def session(self):
        return DatabaseConfig(db_url=self.database_url)

    def setUp(self):
        engine = models.create_engine(self.database_url)
        models.Base.metadata.create_all(engine)
    
    def clear_data(self, model, session, id):
        instance = session.query(model).filter(
            model.id==id
        ).first()
        instance.delete(session=session)
        session.close()
    
    