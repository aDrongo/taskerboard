import os
from flask import Flask, render_template, Response, redirect, url_for, request
from datetime import datetime
import modules.database as db

app = Flask(__name__)



#print(dir(db.session.query()))

#insert_user('ben.gardner','ben.gardner@nwmsrocks.com')
#insert_user('test.uuser','test@nwmsrocks.com')

#update_user('ben.gardner', 'test.user', 'test@nwmsrocks.com')

#delete_user('test.user')

#insert_ticket('test ticket', 'this is a test','tester')
#insert_ticket('test ticket2', 'this is a test','tester')
#insert_ticket('test ticket3', 'this is a test','tester')

#update_ticket(1, False,'tested','this test is complete','tester','')

#insert_comment(1,'ben.gardner','this is the first test comment')
#insert_comment(1,'ben.gardner','this is a second test comment')
#insert_comment(2,'ben.gardner','this is another test comment')

#result = db.query_comments(1)
#for item in result:
    #body, created_at, created_by, id, ticket
#    print(item.body)


@app.route("/")
def home():
    tickets = db.query_tickets_all()

    return render_template("index.html", tickets=tickets)

@app.route("/tickets_open")
def tickets_open():
    tickets = db.query_tickets_open()

    return render_template("tickets.html", tickets=tickets)


@app.route("/ticket/<id>")
def ticket(id):
    ticket = db.query_ticket(id)
    comments = db.query_comments(id)
    return render_template("ticket.html", ticket=ticket, comments=comments)



# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))