from sqlalchemy import create_engine
from sqlalchemy import Integer, String, ForeignKey, Column, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('mysql+pymysql://root:941133109@localhost/contacts_api_db')

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'

    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    contact_fname = Column(String(255), nullable=False)
    contact_lname = Column(String(255), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    contact_email = Column(String(255), nullable=False, unique=True)
    contact_job = Column(String(255), default='not mentioned')
    contact_adr = Column(Text)
    city_id = Column(Integer, ForeignKey('cities.city_id'))
    def __repr__(self):

        return  "contact_fname='{self.contact_fname}', " \
                "contact_lname='{self.contact_lname}', " \
                "contact_phone='{self.contact_phone}', " \
                "contact_email='{self.contact_email}', " \
                "contact_job='{self.contact_job}', " \
                "contact_adr='{self.contact_adr}', " \
                "city_id='{self.city_id}')".format(self=self)


class City(Base):
    __tablename__ = 'cities'

    city_id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(255), nullable=False)
    state_id = Column(Integer, ForeignKey('states.state_id'))

    def __repr__(self):

        return "city_name='{self.city_name}', "\
               "state_id='{self.state_id}', ".format(self=self)

class State(Base):
    __tablename__ = 'states'

    state_id = Column(Integer, primary_key=True, autoincrement=True)
    state_name = Column(String(255), nullable=False, unique=True)

    def __repr__(self):

        return "state_name='{self.state_name}'".format(self=self)
