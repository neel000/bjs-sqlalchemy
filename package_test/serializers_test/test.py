from bjs_sqlalchemy import serializers 
from bjs_sqlalchemy.testclient import TestClient as TS
from .models import TestSerializerModel, TestFileHandleModel
import base64
import os
from typing import List, Type
from pydantic import BaseModel
import asyncio
from sqlalchemy.future import select

class TestClient(TS):
    database_url = "sqlite:///./serializers_test/database.db"
    asyn_database_url = "sqlite+aiosqlite:///./serializers_test/database.db"

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
    
class TestSerializer(serializers.Serializer):
    name:str

    class Meta:
        models = TestSerializerModel
    
    class Config:
        from_attributes = True

class TestFileHandleModelSerializer(serializers.Serializer):
    file:str

    class Meta:
        models = TestFileHandleModel

class ListSerializer:
    def __new__(cls, schema: Type[BaseModel]):
        return serializers.create_model(
        'ListSchema',
        results=(List[schema], [])
    )

class TestIntregration(TestClient):
    model = TestSerializerModel
    serializer = TestSerializer

    def test_blank_data_check(self):
        session = self.session
        assert session.query(TestSerializerModel).count() == 0
        #Read List With Serializer
        query = session.query(self.model).all()
        serializer = ListSerializer(self.serializer)
        srz_data = serializer(results=query)
        self.assertEqual(srz_data.model_dump()['results'], [])

    def test_crud_valid_value(self):
        session = self.session

        #Create
        serializer = self.serializer(name="Test Name")
        status, data = serializer.save(session=session)
        self.assertEqual(status, True)
        self.assertEqual(data.name, "Test Name")
        output = {'id': 1, 'name': 'Test Name'}
        self.assertDictEqual(data.model_dump(), output)

        #Read List With Serializer
        query = session.query(self.model).all()
        serializer = ListSerializer(self.serializer)
        srz_data = serializer(results=query)
        self.assertEqual(srz_data.model_dump()['results'], [output])


        #Read Object With Serializer
        instance = session.query(self.model).filter(self.model.id==data.id).first()
        serializer = self.serializer(**instance.__dict__)
        assert serializer.model_dump() == output

        # Update
        status, update_data = self.serializer(
            name="Update Test Name"
        ).save(session=session, instance=instance)
        self.assertEqual(status, True)
        assert update_data.name == "Update Test Name"
        output["name"] = "Update Test Name"
        self.assertDictEqual(update_data.model_dump(), output)
        #Delete
        self.clear_data(model=self.model, session=session, id=data.id)

class AsyncTestIntregration(TestClient):
    serializer = TestSerializer
    model = TestSerializerModel

    async def async_test_crud_data_check(self):
        session = self.async_session
        #Create
        serializer = self.serializer(name="Test Name")
        status, data = await serializer.async_save(session=session)
        created_id = data.id
        self.assertEqual(status, True)
        self.assertEqual(data.name, "Test Name")
        output = {'id': 1, 'name': 'Test Name'}
        self.assertDictEqual(data.model_dump(), output)

     
        #Read List With Serializer
        query = select(self.model)
        exec_query = await session.execute(query)
        data = exec_query.scalars().all()
        serializer = ListSerializer(self.serializer)
        srz_data = serializer(results=data)
        self.assertEqual(srz_data.model_dump()['results'], [output])

        #Read Object With Serializer
        get_query = select(self.model).filter(self.model.id==created_id)
        exec_query = await session.execute(get_query)
        instance = exec_query.scalars().first()
        serializer = self.serializer(**instance.__dict__)
        assert serializer.model_dump() == output

        # Update
        status, update_data = await self.serializer(
            name="Update Test Name"
        ).async_save(session=session, instance=instance)

        self.assertEqual(status, True)
        assert update_data.name == "Update Test Name"
        output["name"] = "Update Test Name"
        self.assertDictEqual(update_data.model_dump(), output)
        await instance.async_delete(session=session)
        assert self.session.query(self.model).count() == 0
        
class TestFileHandleModelOperation(TestClient):
    model = TestFileHandleModel
    serializer = TestFileHandleModelSerializer

    def load_file(self):
        file_path = "./static/image.jpeg"
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        encoded_file = base64.b64encode(file_content)
        encoded_string = encoded_file.decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded_string}"
        return data_url

    def test_crud_operation(self):
        session = self.session
        assert session.query(self.model).count() == 0
        session.close()
        file = self.load_file()
        serializer = self.serializer(file=file)
        status, data = serializer.save(session=session)
        assert status
        assert os.path.exists(data.file)

        instance = session.query(self.model).filter(self.model.id==data.id).first()
        assert(instance.file == data.file)
        serializer = self.serializer(file=file)
        update_status, update_data = serializer.save(session=session, instance=instance)
        assert not (instance.file == data.file)
        assert update_status
        assert os.path.exists(update_data.file)
        assert not os.path.exists(data.file)

        serializer = self.serializer(file="")
        update_status, update_data = serializer.save(session=session, instance=instance)
        assert not update_status
        self.assertAlmostEqual(update_data, [{'file': 'This value is not be empty'}])

        serializer = self.serializer(file="dfkfjskdjk")
        update_status, update_data = serializer.save(session=session, instance=instance)
        assert not update_status
        self.assertAlmostEqual(update_data, [{'file': 'Error to upload file'}])
        self.clear_data(model=self.model, session=session, id=data.id)
        

