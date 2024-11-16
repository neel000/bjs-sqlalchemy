from bjs_sqlalchemy.tests.model_test.models import (
    TestCharFieldModel, TestCharFieldNullCheck, 
    TestTextFieldModel, TestTextFieldNullCheck,
    TestFileFieldModel, TestFileFieldNullCheck,
    TestIntFieldModel, TestModelCRUD
)
from bjs_sqlalchemy import models
from bjs_sqlalchemy.tests.model_test.db_config import DatabaseConfig
from bjs_sqlalchemy.tests.client import TestClient
import base64
import os


class Common:
    def sort(self, data):
        return sorted(data, key=lambda x: list(x.keys())[0])
    
    async def clear_data(self, model, session, id):
        instance = session.query(model).filter(
            model.id==id
        ).first()
        await instance.delete(session=session)
        session.close()
    
    def load_file(self):
        
        file_path = "./tests/model_test/static/image.jpeg"
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        
        encoded_file = base64.b64encode(file_content)
        encoded_string = encoded_file.decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded_string}"
        return data_url

    def total_data(self, session, model=None):
        model = self.model if model is None else model
        return session.query(model).count()

    def get_instance(self, model=None, id=1):
        session = DatabaseConfig()
        model = model if model else self.model
        return session.query(model).filter(model.id==id).first()


class TestCharFieldModelperation(TestClient, Common):
    model = TestCharFieldModel
    null_model = TestCharFieldNullCheck

    def test_list_test_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()
    
    async def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = await obj.save(session=session)
        except_output = [{'name': 'This value is not be empty'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(name="")
        status, data = await obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output
        session.close()
    
    async def test_create_valid_data(self):
        session = DatabaseConfig()
        obj = self.model(name="Indranil")
        status, data = await obj.save(session=session)
        assert status 
        assert data.name == "Indranil"
        session.close()

        session = DatabaseConfig()
        assert self.total_data(session=session) == 1
        await self.clear_data(model=self.model, session=session, id=data.id)
          
    async def test_null_check_no_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = await obj.save(session=session)
        assert status
        assert data.name is None
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_null_check_blank_data(self):
        session = DatabaseConfig()
        obj = self.null_model(name="")
        status, data = await obj.save(session=session)
        assert status
        assert data.name == ""
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_null_check_valid_data(self):
        session = DatabaseConfig()
        obj = self.null_model(name="hey")
        status, data = await obj.save(session=session)
        assert status
        assert data.name == "hey"
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_update_with_data(self):
        session = DatabaseConfig()
        obj = self.model(name="Testname")
        _, data = await obj.save(session=session)

        session = DatabaseConfig()
        instance = session.query(self.model).filter(self.model.id == data.id).first()
        instance.name = "UpdateTestName"

        _status, update_data = await instance.save(session=session)
        assert _status
        assert update_data.name == "UpdateTestName"
        await self.clear_data(session=session, model=self.model, id=data.id)

class  TestTextFieldModelModelOperation(TestClient, Common):
    model = TestTextFieldModel
    null_model = TestTextFieldNullCheck

    def test_list_test_model(self):
        session = DatabaseConfig()
        self.total_data(session=session) == 0
        session.close()

    async def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = await obj.save(session=session)
        except_output = [{'desc': 'This value is not be empty'}]
        assert not status
        
        assert self.sort(data) == except_output

        obj = self.model(desc="")
        status, data = await obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output
        session.close()

    async def test_create_valid_data(self):
        session = DatabaseConfig()
        obj = self.model(desc="Indranil")
        status, data = await obj.save(session=session)
        assert status 
        assert data.desc == "Indranil"
        session.close()
        session = DatabaseConfig()
        assert self.total_data(session=session) == 1
        await self.clear_data(model=self.model, session=session, id=data.id)
        

    async def test_null_check_no_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = await obj.save(session=session)
        assert status
        assert data.desc is None
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_null_check_blank_data(self):
        session = DatabaseConfig()
    
        obj = self.null_model(desc="")
        status, data = await obj.save(session=session)
        assert status
        assert data.desc == ""
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
        obj = self.null_model()
        status, data = await obj.save(session=session)
        assert status
        assert data.desc is None
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_null_check_valid_data(self):
        session = DatabaseConfig()
        obj = self.null_model(desc="hey")
        status, data = await obj.save(session=session)
        assert status
        assert data.desc == "hey"
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)
    
    async def test_update_with_data(self):
        session = DatabaseConfig()
        obj = self.model(desc="Testname")
        _, data = await obj.save(session=session)

        session = DatabaseConfig()
        instance = session.query(self.model).filter(self.model.id == data.id).first()
        instance.desc = "UpdateTestName"

        _status, update_data = await instance.save(session=session)
        assert _status
        assert update_data.desc == "UpdateTestName"
        await self.clear_data(session=session, model=self.model, id=data.id)
    

class TestFileFieldModelOperation(TestClient, Common):
    model = TestFileFieldModel
    null_model = TestFileFieldNullCheck
    
    def test_list_test_model(self):
        session = DatabaseConfig()
        query = session.query(self.model)
        assert self.total_data(session=session) == 0
        session.close()
    
    async def test_blank_file_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = await obj.save(session=session)
        except_output = [{'image': 'This value is not be empty'}]
        assert  not status
        
        assert self.sort(data) == except_output

        obj = self.model(image="")
        status, data = await obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(image="xcccc")
        status, data = await obj.save(session=session)
        
        except_output = [{'image': 'Error to upload file'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(image="xcc,dfdscc")
        status, data = await obj.save(session=session)
        
        except_output = [{'image': 'Error to upload file'}]
        assert not status
        assert self.sort(data) == except_output

        session.close()
    
    async def test_base64_file_upload(self):
        session = DatabaseConfig()
        file = self.load_file()
        obj = self.model(image=file)
        status, data = await obj.save(session=session)
        prev_path = data.image
        assert status
        assert os.path.exists(prev_path)
        assert self.total_data(session=session) == 1

        status, update = await data.save(session=session)
        assert status
        assert update.image == data.image

        instance = session.query(self.model).filter(self.model.id==data.id).first()

        instance.image = self.load_file()
        status, update_with_image = await instance.save(session=session)
        assert status
        assert update_with_image.image != prev_path
        assert not os.path.exists(prev_path)
        assert os.path.exists(update_with_image.image)
        await self.clear_data(model=self.model, session=session, id=data.id)

    async def test_null_check_blank_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = await obj.save(session=session)

        assert status
        assert data.image is None
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)

        obj = self.null_model(image="")
        status, data = await obj.save(session=session)

        assert status
        assert data.image == ""
        assert self.total_data(session=session, model=self.null_model) == 1
        await self.clear_data(model=self.null_model, session=session, id=data.id)

    async def test_null_base64_file_upload(self):
        session = DatabaseConfig()
        file = self.load_file()
        obj = self.null_model(image=file)
        status, data = await obj.save(session=session)
        assert status
        assert os.path.exists(data.image)
        assert self.total_data(session=session, model=self.null_model) == 1

        status, update = await data.save(session=session)
        assert status
        assert update.image == data.image

        instance = session.query(self.null_model).filter(self.null_model.id==data.id).first()

        instance.image = self.load_file()
        status, update_with_image = await instance.save(session=session)
        assert status
        assert update_with_image.image != data.image
        assert not os.path.exists(data.image)
        assert os.path.exists(update_with_image.image)
        await self.clear_data(model=self.null_model, session=session, id=data.id)

class TestIntFieldModelOprtation(TestClient, Common):
    model = TestIntFieldModel

    def test_list_test_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()
    
    async def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = await obj.save(session=session)
        
        except_output = [{'int_f': 'This value is not be empty'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(int_f="")
        status, data = await obj.save(session=session)
        assert not status
        assert self.sort(data) == except_output
    
    async def test_create_required_int_f_data(self):
        session = DatabaseConfig()
        obj = self.model(int_f=1)
        status, data = await obj.save(session=session)
        assert status 
        assert data.int_f == 1
        assert data.int_f_default == 0
        assert data.int_f_null == None
        session.close()
        assert self.total_data(session=session) == 1
        await self.clear_data(model=self.model, session=session, id=data.id)
        
    async def test_create_with_data(self):
        session = DatabaseConfig()
        obj = self.model(int_f=1, int_f_default=12, int_f_null=5)
        status, data = await obj.save(session=session)
        assert status 
        assert data.int_f == 1
        assert data.int_f_default == 12
        assert data.int_f_null == 5
        session.close()
        assert self.total_data(session=session) == 1
        await self.clear_data(model=self.model, session=session, id=data.id)

class TestModelCRUDOperation(TestClient, Common):
    model = TestModelCRUD

    def test_list_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()

    async def test_create_blank_data(self):
        session = DatabaseConfig()
        instance = self.model()
        status, data = await instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'file_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        instance = self.model(char_f="Indranil")
        status, data = await instance.save(session=session)

        except_output = [
            {'file_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        instance = self.model(int_f=100)
        status, data = await instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'file_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        file = self.load_file()
        instance = self.model(file_f=file)
        status, data = await instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

    async def test_create_required_valid_data(self):
        session = DatabaseConfig()
        payload = {
            'char_f': "String test", 
            'file_f': self.load_file(), 
            'int_f': 1, 
            'text_f': 'Text field test'
        }
        instance = self.model(**payload)
        status, data = await instance.save(session=session)

        assert status
        assert self.total_data(session=session) == 1
        assert data.char_f == payload["char_f"]
        assert data.int_f == payload["int_f"]
        assert data.text_f == payload["text_f"]

        assert data.char_f_null == None
        assert data.int_f_null == None
        assert data.text_f_null == None

        assert os.path.exists(data.file_f)
        await self.clear_data(session=session, model=self.model, id=data.id)

    async def test_create_update_all_valid_data(self):
        session = DatabaseConfig()
        payload = {
            'char_f': "String test", 
            'char_f_null':"String2",
            'file_f': self.load_file(), 
            'file_f_null': self.load_file(), 
            'int_f': 1, 
            'int_f_null': 2, 
            'text_f': 'Text field test',
            'text_f_null': 'Text field test2'
        }
        instance = self.model(**payload)
        status, data = await instance.save(session=session)

        assert status
        assert self.total_data(session=session) == 1
        assert data.char_f == payload["char_f"]
        assert data.int_f == payload["int_f"]
        assert data.text_f == payload["text_f"]

        assert data.char_f_null == payload["char_f_null"]
        assert data.int_f_null == payload["int_f_null"]
        assert data.text_f_null == payload["text_f_null"]

        assert os.path.exists(data.file_f)
        assert os.path.exists(data.file_f_null)

        status, _ = await data.save(session=session)
        assert status

        instance = self.get_instance()
        instance.char_f = "Update char f"
        status, update = await instance.save(session=session)
        assert status
        assert update.char_f != data.char_f
        assert update.char_f == instance.char_f

        instance = self.get_instance()
        instance.file_f = self.load_file()
        status, update = await instance.save(session=session)
        assert status
        assert update.file_f != data.file_f
        
        assert os.path.exists(update.file_f)
        assert not os.path.exists(data.file_f)
        await self.clear_data(session=session, model=self.model, id=data.id)



if __name__ == '__main__':
    # TestCharFieldModelperation().main()
    # TestTextFieldModelModelOperation().main()
    # TestFileFieldModelOperation().main()
    # TestIntFieldModelOprtation().main()
    TestModelCRUDOperation().main()
