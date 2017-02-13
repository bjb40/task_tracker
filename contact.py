"""
dev python 2.7
Wrapper for a contacts database in mysql.
Collects notes and tracks connections (and ties between contacts)

Based on fundamentals from "How to Be a Power Connector: the 5+50+100 Rule" by Judy Robinett.

Bryce Bartlett
"""

from flask import Flask, render_template, g, request, redirect, url_for, flash
import sqlite3, os, datetime

app = Flask(__name__)

#db functions revised from https://github.com/pallets/flask/blob/master/examples/flaskr/flaskr/flaskr.py


# Load default config and override config from an environment variable
app.config.update(dict(
    #DATABASE=os.path.join(app.root_path, 'contacts.db'),
    DATABASE='C:/Users/bjb40/Dropbox/tracker_data/contacts.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.before_request
def before_request():
    g.db = sqlite3.connect("C:/Users/bjb40/Dropbox/tracker_data/contacts.db")

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route("/")
def hello():
    author= "Bryce Bartlett"
    name = "Bryce Bartlett"
    return render_template ('index.html', author=author,name=name)

@app.route('/contacts.html')
def contacts():
    names = g.db.execute("SELECT name FROM card").fetchall()
    return render_template('contacts.html', names=names)

@app.route('/summary.html')
def summary():
    
    today=datetime.date.today()
    levs = g.db.execute('SELECT crossid,circle,followup FROM FREQ').fetchall()
    peeps=dict()
    summ = dict()

    #need to kill the loops if possible

    for l in levs:
        peeps[l[1]] = g.db.execute('SELECT NAME, ID FROM CARD where CIRCLE=?', (l[0],)).fetchall()
        summ[l[1]] = dict()
        #calculate days from last contact
        for i in peeps[l[1]]:
            d=g.db.execute('SELECT MAX(DATE) FROM EVENTS where CONTACT=?', (i[1],)).fetchall()[0][0]
            dt = datetime.datetime.strptime(d,'%Y-%m-%d').date()
            delta = (today - dt).days
            followup = l[2] < delta
            summ[l[1]][i[0]] = (dt,delta)
        
    return render_template('summary.html', summ=summ)

@app.route('/card.html')
def card():
    cname=request.args.get('name','')
    ##need to search from database using the request and update everything
    db=get_db()
    cur=db.execute("SELECT * FROM card WHERE NAME=?", (cname,))
    srch=cur.fetchall()
    keys=srch[0].keys()
    return render_template('contact_card.html',name=srch,keys=keys,action=url_for('update_entry'))

@app.route('/new')
def make_new():
    db=get_db()
    cur=db.execute("select * from card")
    keys=list(map(lambda x: x[0], cur.description))
    keys.remove("ID")
    return render_template('contact_card.html',name=[[""]*len(keys)],keys=keys,action=url_for('add_entry'))

@app.route('/update', methods=['POST'])
def update_entry():
    db = get_db()
    #should simplify
    db.execute('UPDATE card SET NAME=?, EMAIL=?, PHONE=?, NETWORK=?, NOTES=?, JOB=?, INDUSTRY=?, LOCATION=?, ' +
               'CLOSENESS=?, CIRCLE=?, RESOURCES=?, INFLUENCE=? ' +
               'WHERE ID=?',
               [request.form['NAME'],
                request.form['EMAIL'],
                request.form['PHONE'],
                request.form['NETWORK'],
                request.form['NOTES'],
                request.form['JOB'],
                request.form['INDUSTRY'],
                request.form['LOCATION'],
                request.form['CLOSENESS'],
                request.form['CIRCLE'],
                request.form['RESOURCES'],
                request.form['INFLUENCE'],
                request.form['ID']])
    db.commit()
    #return render_template('contact_card.html')
    #flash('New contact created.')
    return redirect(url_for('contacts'))

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    #need to update....
    db.execute('insert into card (NAME, EMAIL, PHONE, NETWORK, NOTES, JOB, INDUSTRY) values (?, ?, ?, ?, ?, ?, ?)',
               [request.form['NAME'],
                request.form['EMAIL'],
                request.form['PHONE'],
                request.form['NETWORK'],
                request.form['NOTES'],
                request.form['JOB'],
                request.form['INDUSTRY']
               ])
    db.commit()
    #return render_template('contact_card.html')
    #flash('New contact created.')
    return redirect(url_for('contacts'))



####
#Event Tracking
####

@app.route('/events.html')
def list_events():
    cname=request.args.get('name','')
    db=get_db()
    cur=db.execute("SELECT ID FROM card where NAME=?",(cname,))
    n_id=cur.fetchall()[0][0]
    cur=db.execute("SELECT * FROM events WHERE CONTACT=?", (n_id,))
    srch=cur.fetchall()
    keys=srch[0].keys()
    return render_template('events.html',name=cname,keys=keys,events=srch)

@app.route('/newevent')
def make_newevent():
    cname=request.args.get('name','')
    db=get_db()
    cur=db.execute("SELECT ID FROM card where NAME=?",(cname,))
    n_id=cur.fetchall()[0][0]
    cur=db.execute("select * from events")
    keys=list(map(lambda x: x[0], cur.description))
    keys.remove("EVENTID")
    nm=[dict(zip(keys,[""]*len(keys)))]
    nm[0]['CONTACT']=n_id
    d=datetime.datetime.now()
    nm[0]['DATE']=d.strftime('%Y-%m-%d')
    #nm[0]['DATE']=d.strftime('%Y-%m-%d %H:%M:%S')
    return render_template('contact_card.html',name=nm,keys=keys,action=url_for('add_event'))

    
@app.route('/addevent', methods=['POST'])
def add_event():
    db = get_db()
    db.execute('insert into events (DATE,CHANNEL,NOTES,CONTACT) values (?, ?, ?, ?)',
               [request.form['DATE'],
                request.form['CHANNEL'],
                request.form['NOTES'],
                request.form['CONTACT'],
               ])
    db.commit()
    n=db.execute('select NAME from card WHERE ID=?', (request.form["CONTACT"]))
    cname=n.fetchall()[0][0]
    return redirect(url_for('list_events',name=cname))
    
if __name__ == "__main__":
    app.run()

with app.test_request_context():
    cname='John Doe'
    u=url_for('list_events',name=cname)
    
#testing 
#with app.test_request_context():
    #    db=get_db()
#    cur=db.execute("SELECT * FROM card WHERE NAME=?", ("John Doe",))
#    srch=cur.fetchall()
#    print srch[0].keys()
    #for row in srch:
    #    print "%S %s" % (row["name"],row["category"])
    #
#    print url_for('card',name='John Doe')
