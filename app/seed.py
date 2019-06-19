# Put it in contact_list directory to work

from app.db import *
import random


Session = sessionmaker(bind=engine)
session = Session()

fnames = ['Lionel', 'Xavi',
          'Jordi', 'Dani',
          'Gerard', 'Carlos',
          'David', 'Sergio']

lnames = ['Messi', 'Hernandez',
          'Alba', 'Alves',
          'Pique', 'Puyol',
          'Villa', 'Busquets']

emails = [fnames[i] + '_' + lnames[i] + '@yahoo.com' for i in range(len(lnames))]

phones = ['0098910', '0098906',
         '0098917', '0098902',
         '0098903', '0098904',
         '0098909', '009805']

jobs = ['Center Forward', 'Center Midfielder',
        'Left Back', 'Right Back',
        'Center Back', 'Center Back',
        'Center Forward', 'Defensive Midfielder']

states = ['Europe', 'America',
          'Asia', 'Africa']

cities = ['Mashhad', 'Tehran',
          'Rome', 'Isfahan',
          'Ankara', 'MamadAbad',
          'Ghale Abkuh!']

adr_chars = [random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) for i in range(20)]

address = ' - '.join(adr_chars)


state_entries = []
city_entries = []

for item in states:
    state = State(state_name=item)
    state_entries.append(state)

state_num = len(state_entries)

"""
for i in range(10):
    states_ids = [i+1 for i in range(len(state_entries))]
    city = random.choice(cities)

    item = City(city_name=city, state_id=random.choice(states_ids))
    city_entries.append(item)

####################################################################
print('Inserting in table --> States')

for entry in state_entries:
    session.add(entry)
    session.commit()

print('Inserting in table --> Cities')

for entry in city_entries:
    session.add(entry)
    session.commit()
"""


contacts = []
city_ids = [i for i in range(1,11)]

for i in range(len(fnames)):
    fname = fnames[i]
    lname = lnames[i]
    phone = phones[i]
    email = emails[i]
    job = jobs[i]

    adr_chars = [random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) for i in range(20)]
    address = ' - '.join(adr_chars)
    city_id = random.choice(city_ids)

    entry = Contact(contact_fname=fname,
                    contact_lname=lname,
                    contact_phone = phone,
                    contact_email=email,
                    contact_job=job,
                    contact_adr=address,
                    city_id = city_id)

    session.add(entry)
    session.commit()
