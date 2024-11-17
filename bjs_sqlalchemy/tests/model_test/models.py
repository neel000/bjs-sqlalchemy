from bjs_sqlalchemy import models
from bjs_sqlalchemy.tests.model_test.db_config import DATABASE_URL


engine = models.create_engine(DATABASE_URL)

class TestCharFieldModel(models.Model):
    __tablename__ = "TestCharFieldModel"
    name = models.CharField(max_length=120)

class TestCharFieldNullCheck(models.Model):
    __tablename__ = "TestCharFieldNullCheck"
    name = models.CharField(max_length=120, nullable=True)

class TestTextFieldModel(models.Model):
    __tablename__ = 'TestTextFieldModel'
    desc = models.TextField()

class TestTextFieldNullCheck(models.Model):
    __tablename__ = "TestTextFieldNullCheck"
    desc = models.TextField(nullable=True)

class TestFileFieldModel(models.Model):
    __tablename__ = "TestFileFieldModel"
    image = models.FileField(upload_to="tests/model_test/media")

class TestFileFieldNullCheck(models.Model):
    __tablename__ = "TestFileFieldNullCheck"
    image = models.FileField(upload_to="tests/model_test/media", nullable=True)

class TestIntFieldModel(models.Model):
    __tablename__ = "TestIntFieldModel"
    int_f = models.IntegerField()
    int_f_null = models.IntegerField(nullable=True)
    int_f_default = models.IntegerField(default=0)

class TestModelCRUD(models.Model):
    __tablename__ = "TestModelCRUD"
    char_f = models.CharField(max_length=30)
    char_f_null = models.CharField(max_length=30, nullable=True)

    int_f = models.IntegerField()
    int_f_null = models.IntegerField(nullable=True)

    bool_f = models.BooleanField(default=False)
    bool_f_null = models.BooleanField(nullable=True)

    file_f = models.FileField(upload_to="tests/model_test/media")
    file_f_null = models.FileField(upload_to="tests/model_test/media/null", nullable=True)

    text_f = models.TextField()
    text_f_null = models.TextField(nullable=True)

models.Base.metadata.create_all(engine)