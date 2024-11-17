from bjs_sqlalchemy import serializers 
from bjs_sqlalchemy.testclient import TestClient as TS
from .models import TestSerializerModel, TestFileHandleModel
import base64
import os

class TestClient(TS):
    database_url = "sqlite:///./serializers_test/database.db"

class TestSerializer(serializers.Serializer):
    name:str

    class Meta:
        models = TestSerializerModel

class TestFileHandleModelSerializer(serializers.Serializer):
    file:str

    class Meta:
        models = TestFileHandleModel

class TestIntregration(TestClient):
    model = TestSerializerModel
    serializer = TestSerializer

    def test_crud_valid_value(self):
        session = self.session
        assert session.query(TestSerializerModel).count() == 0
        serializer = self.serializer(name="Test Name")

        #Create
        status, data = serializer.save(session=session)
        self.assertEqual(status, True)
        self.assertEqual(data.name, "Test Name")
        output = {'id': 1, 'name': 'Test Name'}
        self.assertDictEqual(data.model_dump(), output)

        # Update
        instance = session.query(self.model).filter(self.model.id==data.id).first()
        status, update_data = self.serializer(
            name="Update Test Name"
        ).save(session=session, instance=instance)
        self.assertEqual(status, True)
        assert update_data.name == "Update Test Name"
        output["name"] = "Update Test Name"
        self.assertDictEqual(update_data.model_dump(), output)
        #Delete
        self.clear_data(model=self.model, session=session, id=data.id)
        
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


        
    
   





    



