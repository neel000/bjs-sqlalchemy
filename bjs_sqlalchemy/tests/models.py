import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, declarative_base

class CommonMixin:
    id = Column(Integer, primary_key=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

class NameMixin:
    name = Column(String)

engine = create_engine('sqlite:///./tests/database.db')
Base = declarative_base()

Session = sessionmaker(bind=engine)

class Users(Base, CommonMixin, NameMixin):
    __tablename__ = 'users'
    age = Column(Integer)
    address = relationship("Address", back_populates="user")
    contact = relationship("Contact", back_populates="user")
    
class Address(Base, CommonMixin, NameMixin):
    __tablename__ = 'address'
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users, back_populates="address")

class Contact(Base, CommonMixin, NameMixin):
    __tablename__ = 'contact'
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship(Users, back_populates="contact")
    contact_detail = relationship("ContactDetail", back_populates="contact")
    
class ContactDetail(Base, CommonMixin):
    __tablename__ = 'contact_detail'
    contact_id = Column(Integer, ForeignKey(Contact.id))
    contact_no = Column(String)
    contact_type = Column(String)
    contact = relationship(Contact, back_populates="contact_detail")

# Base.metadata.create_all(engine)
