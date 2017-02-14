##just analyzes summaries of contaxt database for summarizing
#so i can develop stuff outside of Flask ...

#prelims

import sqlite3, os, datetime, pandas as pd

#db connections

DATABASE='C:/Users/bjb40/Dropbox/tracker_data/contacts.db'

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(DATABASE)
    #rv.row_factory = sqlite3.Row
    return rv

g = connect_db().cursor()


#@@@@@@@@@@@@@@@
#Listing contacts
#@@@@@@@@@@@@@@@

today=datetime.date.today()
levs = g.execute('SELECT crossid,circle,followup FROM FREQ').fetchall()
peeps=dict()
summary = dict()

#need to kill the loops if possible

for l in levs:
    peeps[l[1]] = g.execute('SELECT NAME, ID FROM CARD where CIRCLE=? ', (l[0],)).fetchall()
    summary[l[1]] = dict()
    #calculate days from last contact
    for i in peeps[l[1]]:
        d=g.execute('SELECT MAX(DATE) FROM EVENTS where CONTACT=? ORDER BY DATE', (i[1],)).fetchall()[0][0]
        dt = datetime.datetime.strptime(d,'%Y-%m-%d').date()
        delta = (today - dt).days
        followup = l[2] < delta
        summary[l[1]][i[0]] = (str(dt),delta,str(followup))
        
        
