**A simple Tornado Application along with sqlalchemy and alembit.**

A web framework which simulates a simple API that stores contacts with some information about them.

You can use GET method for the address -> localhost:8000/contacts to get all contacts info in the list.

You can add contact_id and use GET method like this: localhost:8000/contacts/2 to get specific contact info.

Use POST with all parameters (except for contact_id) to insert items

Use PUT with all parameters to UPDATE an existing contact.

use DEL and send contact_id to DELETE contact.


Restrictions:

Contact_id must be integer and there has to exist a contact with that id in database.

City_id must be integer and there has to exist a city with that id in database (City table).

limit for length of integer columns is 11 and for characters is 255.
emails must be unique.

None of inputs can be left empty.

{fname, lname, phone and job} inputs can't contain these character {!@#$%^&*()[]{}:;"/\\`-+=|'}




