from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.collections import InstrumentedList
from .fields import File
from sqlalchemy.orm.attributes import get_history
import asyncio

class TableFieldCheck:
    __common_fields = [
        'registry', 'metadata', 'create',
        "bulk_create", "update", "bulk_update",
        "delete", "bulk_delete", "save", "async_save",
        "async_delete"
    ]

    def _is_table_field(self, field):
        return not field.startswith("_") and field not in self.__common_fields and getattr(self, field).__class__ != InstrumentedList

class HandleRemoveFile:
    def _file_remove_handle(self, data):
        for key, value in data.items():
            attr = getattr(self.__table__.c, key)
            attr.remove(value)
        
class FieldValidation(TableFieldCheck):
    
    @property
    def _validate(self):
        data = []
        all_fields = self.__dir__()
        
        for field in all_fields:
            if self._is_table_field(field):
                attr = getattr(self.__table__.c, field)
                if (
                    not getattr(attr, "primary_key") and 
                    not getattr(attr, "default") and 
                    not getattr(attr, "nullable") and  
                    not getattr(self, attr.key)
                ):
                    data.append({attr.key:"This value is not be empty"})
                
        return data
    
    @property
    def _file_upload_handle(self):
        data = {}
        all_fields = self.__dir__()
        error = []
       
        for field in all_fields:
            if self._is_table_field(field):
                
                attr = getattr(self.__table__.c, field)
                file_data = getattr(self, field)
                x = get_history(self, field)
                if (attr.__class__ == File) and file_data and x.added:
                    data[field] = attr.upload(file=file_data)
                    if not data[field]:
                        error.append({field:"Error to upload file"})
                    else:
                        setattr(self, field, data[field])

        return error, data

    @property
    def _validate_data(self):
        
        error = self._validate
        if error:return False, error
        error, data = self._file_upload_handle

        if error:
            self._file_remove_handle(data)
            return False, error
        
        return True, data

class UpdateMethodRemoveFile:
    def _update_method_remove_file_get(self):
        all_fields = self.__dir__()
        data = {}
        for field in all_fields:
            if self._is_table_field(field):
                attr = getattr(self.__table__.c, field)
                file_data = getattr(self, field)

                if (attr.__class__ == File) and file_data:
                    x = get_history(self, field)
                    if x.deleted:
                        data[field] = x.deleted[0]
        
        return data

class DeleteMethodRemoveFile(TableFieldCheck, HandleRemoveFile):
    def _delete_method_remove_file_get(self):
        data = {}
        all_fields = self.__dir__()
        for field in all_fields:
            if self._is_table_field(field):
                attr = getattr(self.__table__.c, field)
                if (attr.__class__ == File):
                    file_data = getattr(self, field)
                    data[field] = file_data
                    
        return self._file_remove_handle(data)


# MODELS CRUD MIXIN #
class CreateMixin(FieldValidation, HandleRemoveFile):

    def create(self, session, refresh=True):
        status, data = self._validate_data
        if not status:
            return self._validate_data
        
        try:
            session.add(self)
            session.commit()
            if refresh:
                session.refresh(self)
            return True, self
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            self._file_remove_handle(data)
            return False, [str(e)]
        
    def bulk_create(self, session, data:list=[]):
        if not data:
            return False, ["Data is not found!"]
        try:
            stmt = insert(self.__class__).values(data)
            result = session.execute(stmt)
            session.commit()
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            return False, str(e)
        session.close()
        return True, result.lastrowid

    async def _async_create(self, session, refresh=True):
        status, data = self._validate_data
        if not status:
            await session.close()
            return status, data

        status, output_data = False, self

        try:
            session.add(self)
            await session.commit()
            if refresh:
                await session.refresh(self)
            status, output_data =  True, self
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            self._file_remove_handle(data)
            status, output_data =  False, [str(e)]
        
        await session.close()
        return status, output_data
        
class UpdateMixin(FieldValidation, UpdateMethodRemoveFile, HandleRemoveFile):
    def update(self, session, refresh=True):
        try:
            
            status, data = self._validate_data
            if not status:
                return self._validate_data
            
            old_data = self._update_method_remove_file_get()
            if refresh:
                session.merge(self)
                session.commit()
            session.refresh(self)
            session.close()
            self._file_remove_handle(old_data)
            return True, self
        
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            self._file_remove_handle(data)
            session.rollback()
            return False, [str(e)]

    def bulk_update(self, session, data:list=[]):
        if not data:
            return False, ["Data is not found!"]
        
        try:
            session.bulk_update_mappings(self.__class__, data)
            session.commit()
            return True, [i["id"] for i in data]
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            return False, str(e)
    
    async def _async_update(self, session, refresh=True):
        status, data = self._validate_data
        if not status:
            await session.close()
            return self._validate_data
            
        old_data = self._update_method_remove_file_get()
        status, output_data = False, self
        
        try:
            await session.merge(self)
            await session.commit()
            if refresh:
                await session.refresh(self)
            self._file_remove_handle(old_data)
            status, output_data =  True, self
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            self._file_remove_handle(data)
            await session.rollback()
            status, output_data  = False, [str(e)]
        
        await session.close()
        return status, output_data
        
       

class DeleteMixin(DeleteMethodRemoveFile):
    def delete(self, session):
        try:
            self._delete_method_remove_file_get()
            session.delete(self)
            session.commit()
            session.close()
            return True, None
        
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            session.close()
            return False, str(e)
    
    async def async_delete(self, session):
        try:
            self._delete_method_remove_file_get()
            await session.delete(self)
            await session.commit()
            await session.close()
            return True, None
        
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            session.rollback()
            session.close()
            return False, str(e)
        
    async def bulk_delete(self, session, data:list=[]):
        if not data:
            return False, "Data is not found!"
        
        session.query(self.__class__).filter(
            self.__class__.id.in_(data)
        ).delete(synchronize_session=False)
        
        session.commit()
        session.close()
        return await self.delete(session, data)

