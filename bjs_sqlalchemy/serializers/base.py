from typing import Optional
import pickle
from pydantic import BaseModel, create_model, model_validator
from typing import Optional, List, Type

class Common:
    @model_validator(mode='before')
    def file_handle(cls, values):
        if not values.__class__ == dict:
            return values
        
        for k, v in values.items():
            if v.__class__.__name__ == "UploadFile":
                values[k] = pickle.dumps(v)
        return values
    
    def _serialize_data(self, instance):
        return self.__class__(**instance.__dict__)

    def _key_value(self):
        data = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if value.__class__ == bytes:
                    value = pickle.loads(value)
                
                data[key] = value

        return data

class BaseSerializer(BaseModel):
    pass

class AsyncSerializerMixin:
    async def is_async_valid(self, session, payload):
        return True, []
    
    async def __create(self, session, refresh):
        model = self.__class__.Meta.models
        payload = self._key_value()
        
        valid, error = await self.is_async_valid(session, payload)
        if not valid:
            return valid, error
        response, data =  await model(**payload).async_save(session=session, refresh=refresh)

        if response:
            data = self._serialize_data(data)
        return response, data
    
    async def __update(self, session, instance, refresh):
        payload = self._key_value()
        valid, error = await self.is_async_valid(session, payload)
        if not valid:
            return valid, error
        
        for key, value in payload.items():
            setattr(instance, key, value)
        
        response, data = await instance.async_save(session=session, refresh=refresh)
        
        if response:
            data = self._serialize_data(instance)

        return response, data
        
    async def async_save(self, session, instance=None, refresh=True):
        return await self.__create(
            session, refresh=refresh
        ) if not instance else await self.__update(
            session, instance, refresh=refresh
        )

class SerializerMixin:
    def is_valid(self, session, payload):
        return True, []

    def __create(self, session, refresh):
        model = self.__class__.Meta.models
        payload = self._key_value()
        valid, error = self.is_valid(session, payload)
        if not valid:
            return valid, error
        
        response, data = model(**payload).save(session=session, refresh=refresh)
        if response:
            data = self._serialize_data(data)

        return response, data
    
    def __update(self, session, instance, refresh):
        payload = self._key_value()
        valid, error = self.is_valid(session, payload)
        if not valid:
            return valid, error
        
        for key, value in payload.items():
            setattr(instance, key, value)
        
        response, data = instance.save(session=session, refresh=refresh)
        
        if response:
            data = self._serialize_data(instance)

        return response, data

    def save(self, session, instance=None, refresh=True):
        return self.__create(
            session, refresh=refresh
        ) if not instance else self.__update(
            session, instance, refresh=refresh
        )

class Serializer(BaseSerializer, SerializerMixin, AsyncSerializerMixin, Common):
    id:Optional[int]=None


class ListPaginationSerializer:
    def __new__(cls, schema: Type[BaseSerializer]):
        return create_model(
        'ListPaginationSerializer',
        pagination=(Optional[dict], None),
        results=(List[schema], [])
    )

