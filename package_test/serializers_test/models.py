from bjs_sqlalchemy import models

class TestSerializerModel(models.Model):
    __tablename__ = "TestSerializerModel"
    name = models.CharField()

class TestFileHandleModel(models.Model):
    __tablename__ = "TestFileHandleModel"
    file = models.FileField(upload_to="media/")
