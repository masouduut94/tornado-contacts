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

    def connect(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def db_empty(self):
        session = self.connect()
        query = session.query(Contact)
        db_empty = query.all() is None
        session.close()
        return db_empty

    def all(self):
        session = self.connect()
        query = session.query(Contact)
        session.close()
        lst_dict = []

        for item in query:
            dicts = item.__dict__
            dicts.pop('_sa_instance_state')
            lst_dict.append(dicts)
        return lst_dict

    def one(self, id):
        session = self.connect()
        query = session.query(Contact).filter(Contact.contact_id == int(id))
        # Check if request exists
        exists = query.scalar() is not None
        reply = {'exists': exists}
        if exists:
            result = query.one()
            session.close()
            dicts = result.__dict__
            dicts.pop('_sa_instance_state')
            reply['contact'] = dicts
            return reply
        else:
            reply['contact'] = dict()
            return reply

    def detect_bad_chars(self):
        unacceptable_chars = list('!@#$%^&*()[]{}:;"/\\`-+=|')
        unacceptable_chars.append("'")

        fname_chars = set(self.contact_fname)
        lname_chars = set(self.contact_lname)
        phone_chars = set(self.contact_phone)
        job_chars = set(self.contact_job)

        bad_character = False
        for char in unacceptable_chars:
            if (char in fname_chars) | (char in lname_chars) | (char in phone_chars) | (char in job_chars):
                bad_character = True

        return bad_character

    def is_null(self):
        condition1 = (self.contact_fname == "") | (self.contact_lname == "")
        condition2 = (self.contact_phone == "") | (self.contact_adr == "")
        condition3 = (self.city_id == "") | (self.contact_email == "")
        return condition1 | condition2 | condition3

    def is_too_long(self):
        char_limit = 255
        int_limit = 15
        input_too_long = (len(self.contact_fname) > char_limit) | (len(self.contact_lname) > char_limit) | \
                         (len(self.contact_email) > char_limit) | (len(self.contact_job) > char_limit) | \
                         (len(self.contact_phone) > int_limit)
        return input_too_long

    def check_city(self):
        session = self.connect()
        isInvalid = session.query(City).filter(City.city_id == self.city_id).scalar() is None
        session.close()
        return isInvalid

    def email_is_unique(self):
        session = self.connect()
        email_is_unique = session.query(Contact).filter(Contact.contact_email == self.contact_email).scalar() is not None
        session.close()
        return email_is_unique

    def del_contact(self, contact_id):
        limit = 11
        if len(str(contact_id)) < limit:
            session = self.connect()
            query = session.query(Contact).filter(Contact.contact_id == int(contact_id))
            exists = query.scalar() is not None
            if exists:
                query.delete()
                session.commit()
                session.close()
                return 'deleted'
            else:
                return 'not_found'

        else:
            return 'invalid'

    def insert(self):
        session = self.connect()
        session.add(self)
        session.commit()
        session.close()
        return True

    def update(self):
        session = self.connect()
        query = session.query(Contact).filter(Contact.contact_id == self.contact_id)
        found = query.scalar() is not None
        if found:
            query = query.one()
            query.contact_fname = self.contact_fname
            query.contact_lname = self.contact_lname
            query.contact_phone = self.contact_phone
            query.contact_email = self.contact_email
            query.contact_job = self.contact_job
            query.contact_adr = self.contact_adr
            query.city_id = self.city_id
            session.commit()
            session.close()
            return True
        else:
            return False


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
