from typing import Optional
import pickle
from pydantic import BaseModel, create_model, model_validator
from typing import Optional, List, Type

class Serializer(BaseModel):
    id:Optional[int]=None


    @model_validator(mode='before')
    def file_handle(cls, values):
        if not values.__class__ == dict:
            return values
        
        for k, v in values.items():
            if v.__class__.__name__ == "UploadFile":
                values[k] = pickle.dumps(v)
        return values
    
    def is_valid(self, session, payload):
        return True, []

    def __serialize_data(self, instance):
        return self.__class__(**instance.__dict__)

    def __key_value(self):
        data = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if value.__class__ == bytes:
                    value = pickle.loads(value)
                
                data[key] = value

        return data

    def __create(self, session):
        model = self.__class__.Meta.models
        payload = self.__key_value()
        valid, error = self.is_valid(session, payload)
        if not valid:
            return valid, error
        
        response, data = model(**payload).save(session=session)
        if response:
            data = self.__serialize_data(data)

        return response, data
    
    def __update(self, session, instance):
        payload = self.__key_value()
        valid, error = self.is_valid(session, payload)
        if not valid:
            return valid, error
        
        for key, value in payload.items():
            setattr(instance, key, value)
        
        response, data = instance.save(session=session)
        
        if response:
            data = self.__serialize_data(instance)

        return response, data

    def save(self, session, instance=None):
        return self.__create(
            session
        ) if not instance else self.__update(
            session, instance
        )

def pagination_response_schema(schema: Type[BaseModel]):
    return create_model(
        'ListSchema',
        pagination=(Optional[dict], None),
        results=(List[schema], [])
    )