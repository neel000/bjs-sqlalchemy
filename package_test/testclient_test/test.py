from bjs_sqlalchemy.testclient import TestClient as TS
from bjs_sqlalchemy import models

class TestClient(TS):
    database_url = "sqlite:///./testclient_test/database.db"
    
class TestModel(models.Model):
    __tablename__ = "TestModel"

class TestModel1(models.Model):
    __tablename__ = "TestModel1"


class TestModelOperation(TestClient):
    def test_crud(self):
        session = self.session
        assert session.query(TestModel).count() == 0
        status, data = TestModel().save(session=session)
        assert status
        assert data.id == 1
        status, data = data.save(session=session)
        self.clear_data(model=TestModel, session=session, id=data.id)

    
    
        
    

