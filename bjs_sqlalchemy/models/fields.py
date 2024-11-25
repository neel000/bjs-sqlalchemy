import os
import re
import random
import base64
from datetime import datetime
from sqlalchemy import Column, Text, String, Integer, Boolean
from sqlalchemy.sql.base import _NoArg
from sqlalchemy.sql.schema import SchemaConst

class File(Column):
    def __init__(
            self, __name_pos = None, __type_pos = None, *args, name = None, 
            type_ = None, autoincrement = "auto", default = _NoArg.NO_ARG, 
            insert_default = _NoArg.NO_ARG, doc = None, key = None, index = None, 
            unique = None, info = None, nullable = SchemaConst.NULL_UNSPECIFIED, 
            onupdate = None, primary_key = False, server_default = None, server_onupdate = None, 
            quote = None, system = False, comment = None, insert_sentinel = False, 
            _omit_from_statements = False, _proxies = None, upload_to:str="",
            **dialect_kwargs
        ):
        super().__init__(
            __name_pos, __type_pos, *args, name=name, type_=type_,
            autoincrement=autoincrement, default=default, insert_default=insert_default,
            doc=doc, key=key, index=index, unique=unique, info=info, nullable=nullable,
            onupdate=onupdate, primary_key=primary_key, server_default=server_default,
            server_onupdate=server_onupdate, quote=quote, system=system, comment=comment,
            insert_sentinel=insert_sentinel, _omit_from_statements=_omit_from_statements,
            _proxies=_proxies, **dialect_kwargs
            )
        self.upload_to = upload_to
    
    def __file_location(self, filename):
        os.makedirs(self.upload_to, exist_ok=True)
        return os.path.join(self.upload_to, filename)

    def _file_name_set(self, filename, count=1):
        file_location = self.__file_location(filename)

        if not os.path.exists(file_location):
            return file_location
        
        name = filename.split(".")
        name[0] = f"{name[0]}-{count}"
        new_filename = ""
        x = 0
        for i in name:
            new_filename = new_filename+i if x ==0 else new_filename+"."+i
            x+=1

        return self._file_name_set(new_filename, count+1)

    async def __file_upload(self, file):
        file_location = self._file_name_set(file.filename)
        
        try:
            with open(file_location, "wb") as file_object:
                file_object.write(await file.read())
                file_object.close()
        except Exception:
            return None
        
        return file_location
    
    def get_filename_from_base64(self, base64_string):
        match = re.match(r'data:(?P<type>[\w/]+);base64,', base64_string)
        if match:
            mime_type = match.group('type')
            mime_to_extension = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/gif': '.gif',
                'application/pdf': '.pdf',
            }
            
            extension = mime_to_extension.get(mime_type, '.bin')
            _random = random.randint(1, 100000)
            filename = f"file_{_random}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
            return self.__file_location(filename)
        else:
            raise ValueError("Invalid base64 string or missing MIME type")

    def __base64_upload(self, base_64:str):
        base_64_data = base_64.split(",")

        if len(base_64_data) < 2:
            return None
        
        try:
            file_location = self.get_filename_from_base64(base_64)
            file_data = base64.b64decode(base_64_data[1])
        except Exception as e:
            
            return None
        
        with open(file_location, "wb") as file:
            file.write(file_data)
            file.close()

        return file_location
    
    def upload(self, file):
        return self.__base64_upload(file)
    
    async def async_upload(self, file):
        if file.__class__.__name__== "UploadFile":
            return await self.__file_upload(file)
        return self.__base64_upload(file)
    
    def remove(self, value):
        if value and os.path.exists(value):
            os.remove(value)

class CharField:
    def __new__(cls, max_length=20, nullable=False, **kwargs):
        return Column(String(max_length), nullable=nullable, **kwargs)

class IntegerField:
    def __new__(cls, nullable=False, **kwargs):
        return Column(Integer, nullable=nullable, **kwargs)

class BooleanField:
    def __new__(cls, nullable=False, **kwargs):
        return Column(Boolean, nullable=nullable, **kwargs)

class TextField:
    def __new__(cls, nullable=False, **kwargs):
        return Column(Text, nullable=nullable, **kwargs)

class FileField:
    def __new__(cls, nullable=False, upload_to="media"):
        return File(Text, nullable=nullable, upload_to=upload_to)

