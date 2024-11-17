from .models import (
    TestCharFieldModel, 
    TestCharFieldNullCheck, 
    TestTextFieldModel, TestTextFieldNullCheck,
    TestFileFieldModel, TestFileFieldNullCheck,
    TestIntFieldModel, TestModelCRUD
)

from .db_config import DatabaseConfig, DATABASE_URL
import unittest

from bjs_sqlalchemy.proxy_request import ProxyRequest
import base64
import os
from bjs_sqlalchemy.filters import FilterSet
from bjs_sqlalchemy.serializers import Serializer


class TestCharFilter(FilterSet):
    class Meta:
        model = TestCharFieldModel
        fields = {
            "name"
        }

class TestCharSerializer(Serializer):
    name:str
    

class TestClient(unittest.TestCase):
    pass

class IntregrationTesting(TestClient):
    model = TestCharFieldModel
    def clear_data(self, model, session, id):
        instance = session.query(model).filter(
            model.id==id
        ).first()
        instance.delete(session=session)
        session.close()

    def test_session(self):
        session = DatabaseConfig()
        assert session
        session.close()

    def test_crud(self):
        session = DatabaseConfig()
        query = session.query(self.model).count()
        self.assertEqual(query, 0)

        # Create Data
        obj = self.model(name="Test Name")
        status, data = obj.save(session=session)
        self.assertEqual(status, True)
        self.assertEqual(data.name, obj.name)

        # UpdateData
        data.name = "Update Test Name"
        status, update_data = data.save(session=session)
        
        self.assertEqual(status, True)
        self.assertNotEqual(update_data.name, "Test Name")
        self.assertEqual(update_data.name, data.name)
        self.clear_data(model=self.model, session=session, id=data.id)


class Common:
    def sort(self, data):
        return sorted(data, key=lambda x: list(x.keys())[0])
    
    def clear_data(self, model, session, id):
        instance = session.query(model).filter(
            model.id==id
        ).first()
        instance.delete(session=session)
        session.close()
    
    def load_file(self):
        file_path = "./model_test/static/image.jpeg"
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        
        encoded_file = base64.b64encode(file_content)
        encoded_string = encoded_file.decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded_string}"
        return data_url

    def total_data(self, session, model=None):
        model = self.model if model is None else model
        # print(session.query(model).first().name)
        return session.query(model).count()

    def get_instance(self, model=None, id=1):
        session = DatabaseConfig()
        model = model if model else self.model
        return session.query(model).filter(model.id==id).first()


class TestCharFieldModelperation(TestClient, Common):
    model = TestCharFieldModel
    null_model = TestCharFieldNullCheck
    filter_class = TestCharFilter

    def test_list_test_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()
    
    def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = obj.save(session=session)
        except_output = [{'name': 'This value is not be empty'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(name="")
        status, data = obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output
        session.close()
    
    def test_create_valid_data(self):
        session = DatabaseConfig()
        obj = self.model(name="Indranil")
        status, data = obj.save(session=session)
        assert status 
        assert data.name == "Indranil"
        session.close()

        session = DatabaseConfig()
        assert self.total_data(session=session) == 1
        self.clear_data(model=self.model, session=session, id=data.id)
          
    def test_null_check_no_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = obj.save(session=session)
        assert status
        assert data.name is None
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_null_check_blank_data(self):
        session = DatabaseConfig()
        obj = self.null_model(name="")
        status, data = obj.save(session=session)
        assert status
        assert data.name == ""
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_null_check_valid_data(self):
        session = DatabaseConfig()
        obj = self.null_model(name="hey")
        status, data = obj.save(session=session)
        assert status
        assert data.name == "hey"
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_update_with_data(self):
        session = DatabaseConfig()
        obj = self.model(name="Testname")
        _, data = obj.save(session=session)

        session = DatabaseConfig()
        instance = session.query(self.model).filter(self.model.id == data.id).first()
        instance.name = "UpdateTestName"

        _status, update_data = instance.save(session=session)
        assert _status
        assert update_data.name == "UpdateTestName"
        self.clear_data(session=session, model=self.model, id=data.id)
    
    def test_filter_with_no_data_no_params(self):
        session = DatabaseConfig()
        query = session.query(self.model)
        params = ProxyRequest('')
        filter_data = self.filter_class(params=params, queryset=query).qs
        assert len(filter_data.all()) == 0
        session.close()


class  TestTextFieldModelModelOperation(TestClient, Common):
    model = TestTextFieldModel
    null_model = TestTextFieldNullCheck

    def test_list_test_model(self):
        session = DatabaseConfig()
        self.total_data(session=session) == 0
        session.close()

    def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = obj.save(session=session)
        except_output = [{'desc': 'This value is not be empty'}]
        assert not status
        
        assert self.sort(data) == except_output

        obj = self.model(desc="")
        status, data = obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output
        session.close()

    def test_create_valid_data(self):
        session = DatabaseConfig()
        obj = self.model(desc="Indranil")
        status, data = obj.save(session=session)
        assert status 
        assert data.desc == "Indranil"
        session.close()
        session = DatabaseConfig()
        assert self.total_data(session=session) == 1
        self.clear_data(model=self.model, session=session, id=data.id)
        

    def test_null_check_no_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = obj.save(session=session)
        assert status
        assert data.desc is None
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_null_check_blank_data(self):
        session = DatabaseConfig()
    
        obj = self.null_model(desc="")
        status, data = obj.save(session=session)
        assert status
        assert data.desc == ""
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
        obj = self.null_model()
        status, data = obj.save(session=session)
        assert status
        assert data.desc is None
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_null_check_valid_data(self):
        session = DatabaseConfig()
        obj = self.null_model(desc="hey")
        status, data = obj.save(session=session)
        assert status
        assert data.desc == "hey"
        session = DatabaseConfig()
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)
    
    def test_update_with_data(self):
        session = DatabaseConfig()
        obj = self.model(desc="Testname")
        _, data = obj.save(session=session)

        session = DatabaseConfig()
        instance = session.query(self.model).filter(self.model.id == data.id).first()
        instance.desc = "UpdateTestName"

        _status, update_data = instance.save(session=session)
        assert _status
        assert update_data.desc == "UpdateTestName"
        self.clear_data(session=session, model=self.model, id=data.id)
    
class TestFileFieldModelOperation(TestClient, Common):
    model = TestFileFieldModel
    null_model = TestFileFieldNullCheck
    
    def test_list_test_model(self):
        session = DatabaseConfig()
        query = session.query(self.model)
        assert self.total_data(session=session) == 0
        session.close()
    
    def test_blank_file_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = obj.save(session=session)
        except_output = [{'image': 'This value is not be empty'}]
        assert  not status
        
        assert self.sort(data) == except_output

        obj = self.model(image="")
        status, data = obj.save(session=session)
        
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(image="xcccc")
        status, data = obj.save(session=session)
        
        except_output = [{'image': 'Error to upload file'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(image="xcc,dfdscc")
        status, data = obj.save(session=session)
        
        except_output = [{'image': 'Error to upload file'}]
        assert not status
        assert self.sort(data) == except_output

        session.close()
    
    def test_base64_file_upload(self):
        session = DatabaseConfig()
        file = self.load_file()
        obj = self.model(image=file)
        status, data = obj.save(session=session)
        prev_path = data.image
        assert status
        assert os.path.exists(prev_path)
        assert self.total_data(session=session) == 1

        status, update = data.save(session=session)
        assert status
        assert update.image == data.image

        instance = session.query(self.model).filter(self.model.id==data.id).first()

        instance.image = self.load_file()
        status, update_with_image = instance.save(session=session)
        assert status
        assert update_with_image.image != prev_path
        assert not os.path.exists(prev_path)
        assert os.path.exists(update_with_image.image)
        self.clear_data(model=self.model, session=session, id=data.id)

    def test_null_check_blank_data(self):
        session = DatabaseConfig()
        obj = self.null_model()
        status, data = obj.save(session=session)

        assert status
        assert data.image is None
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)

        obj = self.null_model(image="")
        status, data = obj.save(session=session)

        assert status
        assert data.image == ""
        assert self.total_data(session=session, model=self.null_model) == 1
        self.clear_data(model=self.null_model, session=session, id=data.id)

    def test_null_base64_file_upload(self):
        session = DatabaseConfig()
        file = self.load_file()
        obj = self.null_model(image=file)
        status, data = obj.save(session=session)
        assert status
        assert os.path.exists(data.image)
        assert self.total_data(session=session, model=self.null_model) == 1

        status, update = data.save(session=session)
        assert status
        assert update.image == data.image

        instance = session.query(self.null_model).filter(self.null_model.id==data.id).first()

        instance.image = self.load_file()
        status, update_with_image = instance.save(session=session)
        assert status
        assert update_with_image.image != data.image
        assert not os.path.exists(data.image)
        assert os.path.exists(update_with_image.image)
        self.clear_data(model=self.null_model, session=session, id=data.id)
class TestIntFieldModelOprtation(TestClient, Common):
    model = TestIntFieldModel

    def test_list_test_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()
    
    def test_blank_data_create(self):
        session = DatabaseConfig()
        obj = self.model()
        status, data = obj.save(session=session)
        
        except_output = [{'int_f': 'This value is not be empty'}]
        assert not status
        assert self.sort(data) == except_output

        obj = self.model(int_f="")
        status, data = obj.save(session=session)
        assert not status
        assert self.sort(data) == except_output
    
    def test_create_required_int_f_data(self):
        session = DatabaseConfig()
        obj = self.model(int_f=1)
        status, data = obj.save(session=session)
        assert status 
        assert data.int_f == 1
        assert data.int_f_default == 0
        assert data.int_f_null == None
        session.close()
        assert self.total_data(session=session) == 1
        self.clear_data(model=self.model, session=session, id=data.id)
        
    def test_create_with_data(self):
        session = DatabaseConfig()
        obj = self.model(int_f=1, int_f_default=12, int_f_null=5)
        status, data = obj.save(session=session)
        assert status 
        assert data.int_f == 1
        assert data.int_f_default == 12
        assert data.int_f_null == 5
        session.close()
        assert self.total_data(session=session) == 1
        self.clear_data(model=self.model, session=session, id=data.id)

class TestModelCRUDOperation(TestClient, Common):
    model = TestModelCRUD

    def test_list_model(self):
        session = DatabaseConfig()
        total = self.total_data(session=session)
        assert total == 0
        session.close()

    def test_create_blank_data(self):
        session = DatabaseConfig()
        instance = self.model()
        status, data = instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'file_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        instance = self.model(char_f="Indranil")
        status, data = instance.save(session=session)

        except_output = [
            {'file_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        instance = self.model(int_f=100)
        status, data = instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'file_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

        file = self.load_file()
        instance = self.model(file_f=file)
        status, data = instance.save(session=session)

        except_output = [
            {'char_f': 'This value is not be empty'}, 
            {'int_f': 'This value is not be empty'}, 
            {'text_f': 'This value is not be empty'}
        ]
        assert not status
        assert self.sort(data) == except_output

    def test_create_required_valid_data(self):
        session = DatabaseConfig()
        payload = {
            'char_f': "String test", 
            'file_f': self.load_file(), 
            'int_f': 1, 
            'text_f': 'Text field test'
        }
        instance = self.model(**payload)
        status, data = instance.save(session=session)

        assert status
        assert self.total_data(session=session) == 1
        assert data.char_f == payload["char_f"]
        assert data.int_f == payload["int_f"]
        assert data.text_f == payload["text_f"]

        assert data.char_f_null == None
        assert data.int_f_null == None
        assert data.text_f_null == None

        assert os.path.exists(data.file_f)
        self.clear_data(session=session, model=self.model, id=data.id)

    def test_create_update_all_valid_data(self):
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
        status, data = instance.save(session=session)

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

        status, _ = data.save(session=session)
        assert status

        instance = self.get_instance()
        instance.char_f = "Update char f"
        status, update = instance.save(session=session)
        assert status
        assert update.char_f != data.char_f
        assert update.char_f == instance.char_f

        instance = self.get_instance()
        instance.file_f = self.load_file()
        status, update = instance.save(session=session)
        assert status
        assert update.file_f != data.file_f
        
        assert os.path.exists(update.file_f)
        assert not os.path.exists(data.file_f)
        self.clear_data(session=session, model=self.model, id=data.id)

