from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db_config import DATABASE_URL


from bjs_sqlalchemy import models

class Base(models.Model):
    __abstract__ = True
    is_deleted = Column(Boolean, default=False, nullable=False)

class NameMixin:
    name = Column(String)



class Users(Base, NameMixin):
    __tablename__ = 'users'
    age = Column(Integer)
    address = relationship("Address", back_populates="user")
    contact = relationship("Contact", back_populates="user")
    
class Address(Base,  NameMixin):
    __tablename__ = 'address'
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users, back_populates="address")

class Contact(Base,  NameMixin):
    __tablename__ = 'contact'
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users, back_populates="contact")
    contact_detail = relationship("ContactDetail", back_populates="contact")
    
class ContactDetail(Base):
    __tablename__ = 'contact_detail'
    contact_id = Column(Integer, ForeignKey(Contact.id))
    contact_no = Column(String)
    contact_type = Column(String)
    contact = relationship(Contact, back_populates="contact_detail")

engine = models.create_engine(DATABASE_URL)
models.Base.metadata.create_all(engine)
