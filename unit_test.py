from application import *
from tornado.testing import AsyncHTTPTestCase
from urllib.parse import urlencode
from tornado import testing
import re
from sqlalchemy import func


def check_json(jsons, pattern):
    return bool(re.search(pattern, jsons.decode('utf-8')))


class TestContact(AsyncHTTPTestCase):
    def get_app(self):
        self.application = Application()
        return self.application

    def setUp(self):
        # Set DB as default
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(Contact)
        query.delete()
        session.commit()
        session.close()
        super(TestContact, self).setUp()

    def testPost(self):
        # Test post command by Web server
        data = {
            'contact_fname': 'masoud',
            'contact_lname': 'mas',
            'contact_phone': '449441654',
            'contact_email': 'masdqawd@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }

        body = urlencode(data)

        ####################################### OK first things first, Does it insert items?

        response = self.fetch(self.get_url(""), method='POST', headers=None, body=body)

        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(Contact).filter(Contact.contact_fname == data['contact_fname'],
                                              Contact.contact_lname == data['contact_lname'],
                                              Contact.contact_phone == data['contact_phone'],
                                              Contact.contact_email == data['contact_email'])
        insert_ok = query.scalar() is not None
        message_ok = check_json(response.body, 'insert done')
        self.assertTrue(True, insert_ok & message_ok)

        ####################################### Is email used before?

        self.setUp()

        ########################## Insert two items to check for repeated email in both items

        data1 = {
            'contact_fname': 'masoud',
            'contact_lname': 'mas',
            'contact_phone': '449441654',
            'contact_email': 'mm@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }

        data2 = {
            'contact_fname': 'mr5gtr5eoud',
            'contact_lname': 'mareg eefeqs',
            'contact_phone': '449441654',
            'contact_email': 'mm@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }

        body1 = urlencode(data1)
        body2 = urlencode(data2)

        response1 = self.fetch(self.get_url(""), method='POST', headers=None, body=body1)
        response2 = self.fetch(self.get_url(""), method='POST', headers=None, body=body2)

        not_two_rows = session.query(func.count(Contact.contact_id)).scalar() == 1
        message = check_json(response2.body, 'used before')
        self.assertTrue(True, not_two_rows & message)

        ######################################### What if data entry is too long?

        self.setUp()

        test_data = data.copy()
        test_data['contact_phone'] = '121321312321321321213213131'
        body = urlencode(test_data)
        response = self.fetch(self.get_url(""), method='POST', headers=None, body=body)
        query = session.query(Contact)
        not_inserted = query.scalar() is None
        message_ok = check_json(response.body, 'too long')
        self.assertTrue(True, not_inserted & message_ok)

        test_data = data.copy()
        ############################################# Test empty values
        self.setUp()

        test_data['contact_fname'] = ''
        body = urlencode(test_data)
        response = self.fetch(self.get_url(""), method='POST', headers=None, body=body)
        query = session.query(Contact)
        not_inserted = query.scalar() is None
        message_ok = check_json(response.body, 'cant be left empty')
        self.assertTrue(True, not_inserted & message_ok)
        data['contact_fname'] = 'ewgwegw'

        # Test invalid city_id

        # Test Non-exist city_id

        # Bad inputs contain \ , / " '

        test_data = data.copy()
        ############################################# Test malformed values
        self.setUp()

        test_data['contact_fname'] = 'efea/*-+-\\'
        body = urlencode(test_data)
        response = self.fetch(self.get_url(""), method='POST', headers=None, body=body)
        query = session.query(Contact)
        not_inserted = query.scalar() is None
        message_ok = check_json(response.body, 'bad input')
        self.assertTrue(True, not_inserted & message_ok)
        data['contact_fname'] = 'ewgwegw'

    def testGet(self):
        self.setUp()
        Session = sessionmaker(bind=engine)
        session = Session()

        data = {
            'contact_id': 1,
            'contact_fname': 'masoud',
            'contact_lname': 'mas',
            'contact_phone': '449441654',
            'contact_email': 'masdqawd@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }
        entry = Contact(contact_id=data['contact_id'],
                        contact_fname=data['contact_fname'],
                        contact_lname=data['contact_lname'],
                        contact_phone=data['contact_phone'],
                        contact_email=data['contact_email'],
                        contact_job=data['contact_job'],
                        contact_adr=data['contact_adr'],
                        city_id=int(data['city_id']))

        session.add(entry)
        session.commit()

        response1 = self.fetch(self.get_url("/contacts"), method='GET', headers=None)
        fetch_ok = check_json(response1.body, 'masoud')
        self.assertTrue(True, fetch_ok)

        response2 = self.fetch(self.get_url("/contacts/1"),
                               method='GET',
                               headers=None)
        fetch_ok = check_json(response2.body, 'masoud')
        self.assertTrue(True, fetch_ok)

        response3 = self.fetch(self.get_url("/contacts/100"),
                               method='GET',
                               headers=None)
        fetch_ok = check_json(response3.body, 'not found')
        self.assertTrue(True, fetch_ok)

        response4 = self.fetch(self.get_url("/contacts/5wergr"),
                               method='GET',
                               headers=None)
        fetch_ok = check_json(response4.body, 'bad input')
        self.assertTrue(True, fetch_ok)

    def testDelete(self):
        self.setUp()
        Session = sessionmaker(bind=engine)
        session = Session()

        data = {
            'contact_id': 1,
            'contact_fname': 'masoud',
            'contact_lname': 'mas',
            'contact_phone': '449441654',
            'contact_email': 'masdqawd@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }
        entry = Contact(contact_id=data['contact_id'],
                        contact_fname=data['contact_fname'],
                        contact_lname=data['contact_lname'],
                        contact_phone=data['contact_phone'],
                        contact_email=data['contact_email'],
                        contact_job=data['contact_job'],
                        contact_adr=data['contact_adr'],
                        city_id=int(data['city_id']))

        session.add(entry)
        session.commit()

        response = self.fetch(self.get_url("/contacts?contact_id=1"),
                               method='DELETE',
                               body=None)

        fetch_ok = check_json(response.body, 'delete done')
        query = session.query(Contact).filter(Contact.contact_id == 1)
        not_exists = query.scalar() is None
        self.assertTrue(True, not_exists & fetch_ok)

        self.setUp()
        response = self.fetch(self.get_url("/contacts?contact_id=3"),
                               method='DELETE',
                               body=None)
        fetch_ok = check_json(response.body, 'not found')
        self.assertTrue(True, fetch_ok)

        self.setUp()
        session.add(entry)
        session.commit()
        response = self.fetch(self.get_url("/contacts?contact_id=3wwgw"),
                              method='DELETE',
                              body=None)
        fetch_ok = check_json(response.body, 'bad input')
        self.assertTrue(True, fetch_ok)

    def testPut(self):
        self.setUp()
        Session = sessionmaker(bind=engine)
        session = Session()

        data = {
            'contact_id': 1,
            'contact_fname': 'masoud',
            'contact_lname': 'mas',
            'contact_phone': '449441654',
            'contact_email': 'masdqawd@gggre.com',
            'contact_job': 'STAR',
            'contact_adr': 'ssd - qefe  - we gweg wgw - ewg',
            'city_id': 2
        }

        test_data = data.copy()
        entry = Contact(contact_id=data['contact_id'],
                        contact_fname=data['contact_fname'],
                        contact_lname=data['contact_lname'],
                        contact_phone=data['contact_phone'],
                        contact_email=data['contact_email'],
                        contact_job=data['contact_job'],
                        contact_adr=data['contact_adr'],
                        city_id=int(data['city_id']))

        session.add(entry)
        session.commit()

        ############################################ Does it edit data at all ??
        test_data['contact_fname'] = 'mohamad'
        body = urlencode(test_data)
        response = self.fetch(self.get_url("/contacts"),
                              method='PUT',
                              headers=None,
                              body=body)
        message = check_json(response.body, 'edition done')
        query = session.query(Contact).filter(Contact.contact_fname == 'mohamad')
        is_edited = query.scalar() is not None
        self.assertTrue(True, message & is_edited)

        test_data = data.copy()
        self.setUp()
        session.add(entry)
        session.commit()

        ##################################### What if contact_id not exist?
        test_data['contact_id'] = 2
        test_data['contact_fname'] = 'mohamad'
        body = urlencode(test_data)
        response = self.fetch(self.get_url("/contacts"),
                              method='PUT',
                              headers=None,
                              body=body)
        message = check_json(response.body, 'not found')
        query = session.query(Contact).filter(Contact.contact_fname == 'mohamad')
        is_not_edited = query.scalar() is not None
        self.assertTrue(True, message & is_not_edited)

        test_data = data.copy()
        ############################################ What if input is empty

        test_data['contact_fname'] = ''
        body = urlencode(test_data)
        response = self.fetch(self.get_url("/contacts"),
                              method='PUT',
                              headers=None,
                              body=body)
        message = check_json(response.body, 'left empty')
        query = session.query(Contact).filter(Contact.contact_fname == '')
        is_not_edited = query.scalar() is not None
        self.assertTrue(True, message & is_not_edited)

        test_data = data.copy()

        ############################################ What if input is too long

        test_data['contact_phone'] = '1212414214124124124141421412414141'
        body = urlencode(test_data)
        response = self.fetch(self.get_url("/contacts"),
                              method='PUT',
                              headers=None,
                              body=body)
        message = check_json(response.body, 'too long')
        query = session.query(Contact).filter(Contact.contact_phone == test_data['contact_phone'])
        is_not_edited = query.scalar() is not None
        self.assertTrue(True, message & is_not_edited)

        test_data = data.copy()

        ################################################# What if city_id is not valid

        test_data['city_id'] = 10
        body = urlencode(test_data)
        response = self.fetch(self.get_url("/contacts"),
                              method='PUT',
                              headers=None,
                              body=body)
        message = check_json(response.body, 'not found')
        query = session.query(Contact).filter(Contact.city_id == test_data['city_id'])
        is_not_edited = query.scalar() is not None
        self.assertTrue(True, message & is_not_edited)

        # What if input `city_id` is not a number
        # What if bad charcters appear in fname, lname, phone

if __name__ == '__main__':
    testing.main()


