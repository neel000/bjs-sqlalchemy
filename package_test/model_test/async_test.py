from .db_config import AsyncDBSession
from .models import (
    TestCharFieldModel, TestFileFieldModel
)
import asyncio
from sqlalchemy import func
from sqlalchemy.future import select
import unittest
import base64
import os


class TestClient(unittest.TestCase):
    def test(self):
        func_list = [fun for fun in self.__dir__() if fun.startswith("async_")]
        for fun in func_list:
            fun = getattr(self, fun)
            asyncio.run((fun()))
        if self.__class__ != TestClient:
            print(f"Async Testcase {len(func_list)} RUN")

class AsyncTestCharOperation(TestClient):
    model = TestCharFieldModel

    async def async_check_session(self):
        session = await AsyncDBSession()
        count_query = select(func.count()).select_from(self.model)
        count_result = await session.execute(count_query)
        self.assertEqual(count_result.scalar_one(), 0)
        await session.close()

    async def get_object(self, id):
        session = await AsyncDBSession()
        query = select(self.model).filter(self.model.id == id)
        data = await session.execute(query)
        instance = data.scalars().first()
        await session.close()
        return instance

    async def async_create_blank_test(self):
        session = await AsyncDBSession()
        obj = self.model()
        status, data = await obj.async_save(session=session)
        assert not status
        assert data == [{'name': 'This value is not be empty'}]
        await session.close()

    async def async_create_valid_test(self):
        session = await AsyncDBSession()
        obj = self.model(name="Test")
        status, data = await obj.async_save(session=session)
        obj_id = data.id
        assert status
        assert data.__dict__["name"] == data.name
        assert await self.get_object(id=obj_id)
        status, data = await data.async_delete(session=session)
        assert status
        assert not await self.get_object(id=obj_id)
        await session.close()

    async def async_update_test(self):
        session = await AsyncDBSession()
        obj = self.model(name="Test")

        _, data = await obj.async_save(session=session)
        instance = await self.get_object(id=data.id)

        status, data = await instance.async_save(session=session, refresh=False)
        assert status
        assert data.name == "Test"
        
        instance.name = ""
        status, data = await instance.async_save(session=session, refresh=False)
        assert not status
        assert data == [{'name': 'This value is not be empty'}]
        await session.close()

        session = await AsyncDBSession()
        instance.name = "Update Test"
        status, data = await instance.async_save(session=session, refresh=False)
        assert status
        assert data.name == "Update Test"
        await instance.async_delete(session=session)
        assert not await self.get_object(id=data.id)
        await session.close()

class AsyncTestFileOperation(TestClient):
    model = TestFileFieldModel
    def load_file(self):
        file_path = "./model_test/static/image.jpeg"
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        
        encoded_file = base64.b64encode(file_content)
        encoded_string = encoded_file.decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded_string}"
        return data_url
    
    async def async_test_blank_file_upload(self):
        session = await AsyncDBSession()
        obj = self.model()
        status, data = await obj.async_save(session=session)
        assert not status
        self.assertEqual(data, [{'image': 'This value is not be empty'}])

        obj = self.model(image="fkfjhfjkfj")
        status, data = await obj.async_save(session=session)
        assert not status
        self.assertEqual(data, [{'image': 'Error to upload file'}])
        await session.close()

    
    async def async_test_base64_file_upload(self):
        session = await AsyncDBSession()
        file = self.load_file()
        obj = self.model(image=file)
        status, data = await obj.async_save(session=session)
        prev_path = data.image
        assert status
        assert os.path.exists(prev_path)
        await data.async_delete(session=session)
        assert not os.path.exists(prev_path)


