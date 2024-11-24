from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.collections import InstrumentedList
from .fields import File
from sqlalchemy.orm.attributes import get_history

class TableFieldCheck:
    __common_fields = [
        'registry', 'metadata', 'create',
        "bulk_create", "update", "bulk_update",
        "delete", "bulk_delete", "save", "async_save",
        "async_delete"
    ]

    def _is_table_field(self, field):

        table_field = (
            not field.startswith("_") 
            and field not in self.__common_fields 
        )
        
        if not table_field:return False
        

        try:
            attr = getattr(self.__table__.c, field)
            return attr
        except:
            return False
 

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
            attr = self._is_table_field(field)
            
            if (
                not attr == False and
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
            attr = self._is_table_field(field)

            if not attr == False:
                file_data = getattr(self, field)
                if file_data.__class__.__name__== "UploadFile":
                    error.append(
                        {field:"File field is failed to upload, use async_save method "}
                    )
                    return error, data
                
                x = get_history(self, field)
                
                if (attr.__class__ == File) and file_data and x.added:
                    data[field] = attr.upload(file=file_data)
                    if not data[field]:
                        error.append({field:"Error to upload file"})
                    else:
                        setattr(self, field, data[field])

        return error, data

    @property
    async def _async_file_upload_handle(self):
        data = {}
        all_fields = self.__dir__()
        error = []

        for field in all_fields:
            attr = self._is_table_field(field)
            if not attr == False:
                file_data = getattr(self, field)
                
                x = get_history(self, field)
                
                if (attr.__class__ == File) and file_data and x.added:
                    data[field] = await attr.async_upload(file=file_data)
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

    @property
    async def _async_validate_data(self):
        error = self._validate
        if error:return False, error
        error, data = await self._async_file_upload_handle

        if error:
            self._file_remove_handle(data)
            return False, error
        
        return True, data

class UpdateMethodRemoveFile:
    def _update_method_remove_file_get(self):
        all_fields = self.__dir__()
        data = {}
        for field in all_fields:
            attr = self._is_table_field(field)
            if not attr == False:
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
            attr = self._is_table_field(field)
            if not attr is False and attr.__class__ == File:
                file_data = getattr(self, field)
                data[field] = file_data

        return self._file_remove_handle(data)


# MODELS CRUD MIXIN #
class CreateMixin(FieldValidation, HandleRemoveFile):

    def create(self, session, refresh=True):
        status, data = self._validate_data
        if not status:
            return status, data
        
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
        status, data = await self._async_validate_data
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
            await session.rollback()
            self._file_remove_handle(data)
            status, output_data =  False, [str(e)]
        
        await session.close()
        return status, output_data
        
class UpdateMixin(FieldValidation, UpdateMethodRemoveFile, HandleRemoveFile):
    def update(self, session, **_):
        status, data = self._validate_data
        if not status:
            return status, data
        old_data = self._update_method_remove_file_get()
    
        try:
            session.merge(self)
            session.commit()

            try:session.refresh(self)
            except:...

            session.close()
            self._file_remove_handle(old_data)
            return True, self
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            self._file_remove_handle(data)
            session.rollback()
            return False, [str(e)]

    async def _async_update(self, session, **_):
        status, data = await self._async_validate_data
        if not status:
            await session.close()
            return status, data
            
        old_data = self._update_method_remove_file_get()
        status, output_data = False, self
        
        try:
            await session.merge(self)
            await session.commit()

            try: await session.refresh(self)
            except:...

            self._file_remove_handle(old_data)
            status, output_data =  True, self
        except (SQLAlchemyError, IntegrityError, Exception) as e:
            self._file_remove_handle(data)
            await session.rollback()
            status, output_data  = False, [str(e)]
        
        await session.close()
        return status, output_data

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
    
class DeleteMixin(DeleteMethodRemoveFile):
    def delete(self, session):
        self._delete_method_remove_file_get()
        try:
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
            await session.rollback()
            await session.close()
            return False, str(e)
        
    def bulk_delete(self, session, data:list=[]):
        if not data:
            return False, "Data is not found!"
        
        session.query(self.__class__).filter(
            self.__class__.id.in_(data)
        ).delete(synchronize_session=False)
        
        session.commit()
        session.close()
        return True, None

