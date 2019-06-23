# A simple Tornado Application along with sqlalchemy and alembit

A simple web framework which simulates an API that stores contacts with some information about them. there also exist different unit test cases for errors that has to be catched.

## How to test framework methods

** GET method **

1 : get all contacts info in the list.
example ==> localhost:8000/contacts  | GET

2 : get one contact info (mention contact_id)
example ==> localhost:8000/contacts/1  | GET

** POST method **

1 : insert new contact in database.
example ==> localhost:8000/contacts  | POST

message body : {contact_fname='Tom' , contact_lname='Hardy', contact_phone='41498498', contact_adr= 'somewhere', contact_email='Tom_Hardy@gmail.com', contact_job='jobless', city_id='3'}

** PUT method **

1 : Update existing contact in DB
example ==> localhost:8000/contacts  | POST

message body : {contact_id='1', contact_fname='Tom' , contact_lname='Hardy', contact_phone='41498498', contact_adr= 'somewhere', contact_email='Tom_Hardy@gmail.com', contact_job='jobless', city_id='3'}


** DEL method **

1 : Delete a contact based on recieved contact_id
example ==> localhost:8000/contacts  | POST

message body : {contact_fname='Tom' , contact_lname='Hardy', contact_phone='41498498', contact_adr= 'somewhere', contact_email='Tom_Hardy@gmail.com', contact_job='jobless', city_id='3'}


### Restrictions:

1- 'Contact_id' must be integer and there has to exist a contact with that id in database.

2- 'City_id' must be integer and there has to exist a city with that id in database (City table).

3- limit for length of integer columns is 11 and for characters is 255.

4- 'emails' must be unique.

5- None of method specific params can be left empty.

6- {fname, lname, phone and job} inputs can't contain these character {!@#$%^&*()[]{}:;"/\\`-+=|'}




