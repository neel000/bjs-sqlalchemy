from bjs_sqlalchemy.testclient import TestClient as TS
from bjs_sqlalchemy import models
import asyncio
from sqlalchemy.future import select
from sqlalchemy import func

class TestClient(TS):
    database_url = "sqlite:///./testclient_test/database.db"
    
    asyn_database_url = "sqlite+aiosqlite:///./testclient_test/database.db"

    def test_async(self):
        func_list = [fun for fun in self.__dir__() if fun.startswith("async_test_")]
        for fun in func_list:
            fun = getattr(self, fun)
            asyncio.run((fun()))
        if self.__class__ != TestClient:
            print(f"{self.__class__.__name__} {len(func_list)} Async RUN")
    
    def clear_data(self, model, session, id):
        instance = session.query(model).filter(
            model.id==id
        ).first()
        instance.delete(session=session)
        session.close()
    
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
    
    async def async_test_crud(self):
        session = self.async_session
        count_query = select(func.count()).select_from(TestModel)
        count_result = await session.execute(count_query)
        count = count_result.scalar_one()
        self.assertEqual(count, 0)
        
        obj = TestModel()
        status, data = await obj.async_save(session=session)
        assert status
        assert data.id == 1

        count_result = await session.execute(count_query)
        count = count_result.scalar_one()
        self.assertEqual(count, 1)

        status, data = await data.async_delete(session=session)
        assert status

        count_result = await session.execute(count_query)
        count = count_result.scalar_one()
        self.assertEqual(count, 0)

