"""
dev python 2.7
Wrapper for a contacts database in mysql.
Collects notes and tracks connections (and ties between contacts)

Bryce Bartlett
"""

from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)

#db functions taken from https://github.com/pallets/flask/blob/master/examples/flaskr/flaskr/flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'contacts.db'),
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
    g.db = sqlite3.connect("contacts.db")

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
    ##should edit this to generate and inpute url automatically (otherwise lots of cut/paste)
    return render_template('contacts.html', names=names)

@app.route('/card.html')
def card():
    cname=request.args.get('name','')
    ##need to search from database using the request and update everything
    db=get_db()
    cur=db.execute("SELECT * FROM card WHERE NAME=?", (cname,))
    srch=cur.fetchall()
    keys=srch[0].keys()
    return render_template('contact_card.html',name=srch,keys=keys)

if __name__ == "__main__":
    app.run()

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
