import tornado.ioloop
import tornado.options
import tornado.web
import json
import pandas as pd
from app.db import *
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

def IsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Application(tornado.web.Application):
    def __init__(self):
        regex_number = r"/(\d+)"
        regex_word = r"/(\w+)"
        handlers = [
            (r"/contacts", Contacts),
            (r"/contacts" + regex_word, Contacts)
        ]
        settings = dict(
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class Contacts(tornado.web.RequestHandler):
    def get(self, input=None):
    	print("MASTER BRANCH")
        # All Contacts / one Contact
        if input == None:
            # List all contact
            Session = sessionmaker(bind=engine)
            session = Session()
            query = session.query(Contact)
            db_empty = query.all() is None

            # DB empty ?
            if db_empty == False:
                query = query.all()
                session.close()
                lst_dict = []

                for item in query:
                    dicts = item.__dict__
                    dicts.pop('_sa_instance_state')
                    lst_dict.append(dicts)

                response = json.dumps(lst_dict)
                self.set_status(200, "contacts retrieved")
                self.write(response)
            else:
                # No data in DB
                self.set_status(400, "not found")
                response = json.dumps('{ "Message" : "not found"}')
                self.write(response)

        else:
            # List one contact
            if IsInt(input) == True:
                Session = sessionmaker(bind=engine)
                session = Session()
                query = session.query(Contact).filter(Contact.contact_id == int(input))
                # Check if request exists
                exists = query.scalar() is not None
                if exists == True:
                    result = query.one()
                    session.close()
                    dicts = result.__dict__
                    dicts.pop('_sa_instance_state')
                    js = json.dumps(dicts)
                    self.set_status(200, 'contact retrieved')
                else:
                    self.set_status(400, 'not found')
                    js = json.dumps('{"Message" : "not found"}')
            else:
                self.set_status(401, 'bad input')
                js = json.dumps('{"Message":"bad input"}')
            self.write(js)

    def post(self):
        # Read Arguments
        contact_fname = self.get_argument('contact_fname', '').strip()
        contact_lname = self.get_argument('contact_lname', '').strip()
        contact_phone = self.get_argument('contact_phone', '').strip()
        contact_email = self.get_argument('contact_email', '').strip()
        contact_job   = self.get_argument('contact_job', '').strip()
        contact_adr	  = self.get_argument('contact_adr', '').strip()
        city_id       = self.get_argument('city_id', '').strip()

        char_limit = 255
        int_limit = 15

        ## Check if entries for nullable columns are NULL or not (fname, lname, email, city_id)

        input_empty = (contact_fname == "") | (contact_lname == "") | \
                      (contact_phone == "") | (contact_adr == "") | \
                      (city_id == "") | (contact_email == "")


        ## Check lengths of inputs
        input_too_long = (len(contact_fname) > char_limit) | \
                         (len(contact_lname) > char_limit) | \
                         (len(contact_email) > char_limit) | \
                         (len(contact_job)   > char_limit) | \
                         (len(contact_phone) > int_limit)


        # Check if entries contain values like !,#,^,%,*,(), -, +, \
        unacceptable_chars = list('!@#$%^&*()[]{}:;"/\\`-+=|')
        unacceptable_chars.append("'")

        fname_chars = set(contact_fname)
        lname_chars = set(contact_lname)
        phone_chars = set(contact_phone)

        input_bad_character = False
        for char in unacceptable_chars:
            if (char in fname_chars) | (char in lname_chars) | (char in phone_chars):
                input_bad_character = True

        Session = sessionmaker(bind=engine)
        session = Session()
        email_not_unique = session.query(Contact).filter(Contact.contact_email == contact_email).scalar() is not None

        city_id_is_int = IsInt(city_id)

        if input_empty == True:
            self.set_status(400, 'empty given')
            js = json.dumps('{"Message":"bad input - {fname, lname, phone, email, city_id} cant be left empty"}')
            session.close()
            self.write(js)
        else:

            if input_too_long == True:
                self.set_status(401, 'too long input')
                js = json.dumps('{"Message":"input given is too long"}')
                session.close()
                self.write(js)
            else:

                if input_bad_character == True:
                    self.set_status(402, 'bad input')
                    js = json.dumps('{"Message":"bad input for one of {fname, lname, phone}"}')
                    session.close()
                    self.write(js)

                else:
                    if email_not_unique == True:
                        self.set_status(403, 'email not unique')
                        js = json.dumps('{"Message":"email is used before"}')
                        session.close()
                        self.write(js)

                    else:
                        if city_id_is_int == True:
                            invalid_city_id = session.query(City).filter(City.city_id == city_id).scalar() is None

                            if invalid_city_id == True:
                                self.set_status(404, 'City not found')
                                js = json.dumps('{"Message":"City not found"}')
                                session.close()
                                self.write(js)

                            else:
                                entry = Contact(contact_fname=contact_fname,
                                                contact_lname=contact_lname,
                                                contact_phone=contact_phone,
                                                contact_email=contact_email,
                                                contact_job=contact_job,
                                                contact_adr=contact_adr,
                                                city_id=int(city_id))

                                session.add(entry)
                                session.commit()
                                session.close()
                                self.set_status(200, 'insert done')
                                js = json.dumps('{"Message":"insert done"}')
                                self.write(js)
                        else:
                            self.set_status(405, 'City id is not valid')
                            js = json.dumps('{"Message":"invalid city id"}')
                            session.close()
                            self.write(js)


        ## Check if entries for non-nullable columns are NULL or not (fname, lname, email, city_id)
        ## Check lengths of inputs
        # Check if entries contain values like !,#,^,%,*,(), -, +, \
        # Check email is Unique
        # integer inputs Convertible to int
        # Check city_id exists in city.city_id
        # strip spaces for entries

    def delete(self):
        contact_id = self.get_argument('contact_id', '')
        if IsInt(contact_id) == True:
            contact_id_limit = 11
            if len(str(contact_id)) < contact_id_limit:
                Session = sessionmaker(bind=engine)
                session = Session()
                query = session.query(Contact).filter(Contact.contact_id == int(contact_id))
                exists = query.scalar() is not None
                if exists == True:
                    query.delete()
                    session.commit()
                    session.close()
                    self.set_status(200, 'delete done')
                    js = json.dumps('{"Message":"delete done"}')
                    self.write(js)
                else:
                    self.set_status(400, 'not found')
                    js = json.dumps('{"Message":"not found"}')
                    self.write(js)

            else:
                self.set_status(401, 'contact_id is not valid')
                js = json.dumps('{"Message":"contact_id is not valid"}')
                self.write(js)
        else:
            js = json.dumps('{"Message":"bad input"}')
        self.set_status(402, 'bad input')
        self.write(js)

    def put(self):
        contact_id    = self.get_argument('contact_id', '').strip()
        contact_fname = self.get_argument('contact_fname', '').strip()
        contact_lname = self.get_argument('contact_lname', '').strip()
        contact_phone = self.get_argument('contact_phone', '').strip()
        contact_email = self.get_argument('contact_email', '').strip()
        contact_job = self.get_argument('contact_job', '').strip()
        contact_adr = self.get_argument('contact_adr', '').strip()
        city_id = self.get_argument('city_id', '').strip()

        char_limit = 255
        int_limit = 15

        ## Check if entries for nullable columns are NULL or not (fname, lname, email, city_id)

        input_empty = (contact_fname == "") | (contact_lname == "") | \
                      (contact_phone == "") | (contact_adr == "") | \
                      (city_id == "") | (contact_email == "")

        ## Check lengths of inputs
        input_too_long = (len(contact_fname) > char_limit) | \
                         (len(contact_lname) > char_limit) | \
                         (len(contact_email) > char_limit) | \
                         (len(contact_job) > char_limit) | \
                         (len(contact_phone) > int_limit) | len(str(contact_id)) > 11

        # Check if entries contain values like !,#,^,%,*,(), -, +, \
        unacceptable_chars = list('!@#$%^&*()[]{}:;"/\\`-+=|')
        unacceptable_chars.append("'")

        fname_chars = set(contact_fname)
        lname_chars = set(contact_lname)
        phone_chars = set(contact_phone)

        input_bad_character = False
        for char in unacceptable_chars:
            if (char in fname_chars) | (char in lname_chars) | (char in phone_chars):
                input_bad_character = True

        Session = sessionmaker(bind=engine)
        session = Session()
        email_not_unique = session.query(Contact).filter(Contact.contact_email == contact_email).scalar() is not None

        city_id_is_int = IsInt(city_id)

        if input_empty == True:
            self.set_status(400, 'empty given')
            js = json.dumps('{"Message":"bad input - {fname, lname, phone, email, city_id} cant be left empty"}')
            session.close()
            self.write(js)
        else:

            if input_too_long == True:
                self.set_status(401, 'too long input')
                js = json.dumps('{"Message":"input given is too long"}')
                session.close()
                self.write(js)
            else:

                if input_bad_character == True:
                    self.set_status(402, 'bad input')
                    js = json.dumps('{"Message":"bad input for one of {fname, lname, phone}"}')
                    session.close()
                    self.write(js)

                else:
                    if email_not_unique == True:
                        self.set_status(403, 'email not unique')
                        js = json.dumps('{"Message":"email is used before"}')
                        session.close()
                        self.write(js)

                    else:
                        if city_id_is_int == True:
                            invalid_city_id = session.query(City).filter(City.city_id == city_id).scalar() is None

                            if invalid_city_id == True:
                                self.set_status(404, 'City not found')
                                js = json.dumps('{"Message":"City not found"}')
                                session.close()
                                self.write(js)

                            else:
                                query = session.query(Contact).filter(Contact.contact_id == contact_id)
                                exists = query.scalar() is not None
                                if exists == True:
                                    query = query.one()
                                    query.contact_fname = contact_fname
                                    query.contact_lname = contact_lname
                                    query.contact_phone = contact_phone
                                    query.contact_email = contact_email
                                    query.contact_job = contact_job
                                    query.contact_adr = contact_adr
                                    query.city_id = city_id

                                    session.commit()
                                    session.close()
                                    self.set_status(200, 'edition done')
                                    js = json.dumps('{"Message":"edition done"}')
                                    session.close()
                                    self.write(js)

                                else:
                                    self.set_status(405, 'not found')
                                    js = json.dumps('{"Message":"not found"}')
                                    session.close()
                                    self.write(js)
                        else:
                            self.set_status(406, 'City id is not valid')
                            js = json.dumps('{"Message":"invalid city id"}')
                            session.close()
                            self.write(js)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
