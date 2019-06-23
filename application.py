from tornado import ioloop, web
import json
from app.db import *
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


def IsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Application(web.Application):
    def __init__(self):
        regex_word = r"/(\w+)"
        handlers = [
            (r"/contacts", Contacts),
            (r"/contacts" + regex_word, Contacts)
        ]
        settings = dict(
            debug=True
        )
        web.Application.__init__(self, handlers, **settings)


class Contacts(web.RequestHandler):

    def initialize(self):
        self.table = Contact()

    def get(self, input=None):
        # All Contacts / one Contact
        if input is None:
            # DB empty ?
            if not self.table.db_empty():
                contacts = self.table.all()
                response = json.dumps(contacts)
                self.set_status(200, "contacts retrieved")
                self.write(response)
            else:
                # No data in DB
                self.set_status(400, "not found")
                response = json.dumps('{ "Message" : "not found"}')
                self.write(response)

        else:
            # List one contact
            if IsInt(input):
                result = self.table.one(input)
                # Check if request exists
                if result['exists']:
                    js = json.dumps(result['contact'])
                    self.set_status(200, 'contact retrieved')
                else:
                    self.set_status(400, 'not found')
                    js = json.dumps('{"Message" : "not found"}')
            else:
                self.set_status(401, 'bad input')
                js = json.dumps('{"Message":"bad input"}')
            self.write(js)

    def post(self):
        city_id = self.get_argument('city_id', '')

        if IsInt(city_id):
            self.table = Contact(contact_fname=self.get_argument('contact_fname', ''),
                                 contact_lname=self.get_argument('contact_lname', ''),
                                 contact_phone=self.get_argument('contact_phone', ''),
                                 contact_email=self.get_argument('contact_email', ''),
                                 contact_job=self.get_argument('contact_job', ''),
                                 contact_adr=self.get_argument('contact_adr', ''),
                                 city_id=int(self.get_argument('city_id', '')))

            is_null = self.table.is_null()
            input_too_long = self.table.is_too_long()
            input_bad_character = self.table.detect_bad_chars()
            email_is_unique = self.table.email_is_unique()
            invalid_city_id = self.table.check_city()

            if is_null:
                self.set_status(400, 'empty given')
                js = json.dumps('{"Message":"bad input - {fname, lname, phone, email, city_id} cant be left empty"}')
                self.write(js)

            elif input_too_long:
                self.set_status(401, 'too long input')
                js = json.dumps('{"Message":"input given is too long"}')
                self.write(js)

            elif input_bad_character:
                self.set_status(402, 'bad input')
                js = json.dumps('{"Message":"bad input for one of {fname, lname, phone}"}')
                self.write(js)

            elif email_is_unique:
                self.set_status(403, 'email not unique')
                js = json.dumps('{"Message":"email is used before"}')
                self.write(js)

            elif invalid_city_id:
                self.set_status(404, 'City not found')
                js = json.dumps('{"Message":"City not found"}')
                self.write(js)

            else:
                self.table.insert()
                self.set_status(200, 'insert done')
                js = json.dumps('{"Message":"insert done"}')
                self.write(js)
        else:
            self.set_status(405, 'City id is not valid')
            js = json.dumps('{"Message":"invalid city id"}')
            self.write(js)

    def delete(self):
        contact_id = self.get_argument('contact_id', '')
        if IsInt(contact_id):
            limit = 11
            result = self.table.del_contact(contact_id)

            if result == 'invalid':
                self.set_status(401, 'contact_id is not valid')
                js = json.dumps('{"Message":"contact_id is not valid"}')
                self.write(js)
            elif result == 'not_found':
                self.set_status(400, 'not found')
                js = json.dumps('{"Message":"not found"}')
                self.write(js)
            elif result == 'deleted':
                self.set_status(200, 'delete done')
                js = json.dumps('{"Message":"delete done"}')
                self.write(js)
        else:
            js = json.dumps('{"Message":"bad input"}')
            self.set_status(402, 'bad input')
            self.write(js)

    def put(self):

        contact_id = self.get_argument('contact_id', '')
        city_id = self.get_argument('city_id', '')
        contact_id_ok = IsInt(contact_id)
        city_id_ok = IsInt(city_id)

        if contact_id_ok & city_id_ok:
            self.table = Contact(contact_id=int(contact_id),
                                 contact_fname=self.get_argument('contact_fname', ''),
                                 contact_lname=self.get_argument('contact_lname', ''),
                                 contact_phone=self.get_argument('contact_phone', ''),
                                 contact_email=self.get_argument('contact_email', ''),
                                 contact_job=self.get_argument('contact_job', ''),
                                 contact_adr=self.get_argument('contact_adr', ''),
                                 city_id=int(self.get_argument('city_id', '')))

            is_null = self.table.is_null()
            input_too_long = self.table.is_too_long()
            input_bad_character = self.table.detect_bad_chars()
            email_is_unique = self.table.email_is_unique()
            invalid_city_id = self.table.check_city()

            if is_null:
                self.set_status(400, 'empty given')
                js = json.dumps('{"Message":"bad input - {fname, lname, phone, email, city_id} cant be left empty"}')
                self.write(js)

            elif input_too_long:
                self.set_status(401, 'too long input')
                js = json.dumps('{"Message":"input given is too long"}')
                self.write(js)

            elif input_bad_character:
                self.set_status(402, 'bad input')
                js = json.dumps('{"Message":"bad input for one of {fname, lname, phone}"}')
                self.write(js)

            elif email_is_unique:
                self.set_status(403, 'email not unique')
                js = json.dumps('{"Message":"email is used before"}')
                self.write(js)

            elif invalid_city_id:
                self.set_status(404, 'City not found')
                js = json.dumps('{"Message":"City not found"}')
                self.write(js)

            else:
                if self.table.update():
                    self.set_status(200, 'insert done')
                    js = json.dumps('{"Message":"insert done"}')
                    self.write(js)

                else:
                    self.set_status(406, 'not found')
                    js = json.dumps('{"Message":"not found"}')
                    self.write(js)

        else:
            self.set_status(405, 'city_id or contact_id is not integer')
            js = json.dumps('{"Message":"city_id or contact_id is not integer"}')
            self.write(js)


def main():
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
