import os
import time
from flask import Flask, render_template, Response, redirect, url_for, request, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField
from datetime import datetime
import modules.database as db

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class CommentForm(Form):
    comment = TextAreaField('Comment:')

class TicketForm(Form):
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=['High','Medium','Low'])
    category = SelectField('Category', choices=['Ticket','Project','WishList'])
    status = SelectField('Status', choices=['Open','Working','Waiting','Closed'])

def ticket_options(option):
    if option == 'all':
        tickets = db.query_tickets_all()
    elif option == 'open':
        tickets = db.query_tickets_open()
    elif option == 'working':
        tickets = db.query_tickets_working()
    elif option == 'waiting':
        tickets = db.query_tickets_waiting()
    elif option == 'closed':
        tickets = db.query_tickets_closed()
    else:
        tickets = db.query_tickets_all()
    return tickets

@app.route("/", methods=['GET','POST'])
def home():
    tickets = db.query_tickets_all()

    return render_template("index.html", tickets=tickets)

@app.route("/ticket/<option>", methods=['GET','POST'])
def tickets(option):
    tickets = ticket_options(option)
    
    if request.method == 'POST':
        pass

    return render_template("tickets.html", option=option, tickets=tickets)


@app.route("/ticket/<option>/<id>", methods=['GET','POST'])
def ticket(option, id):
    tickets = ticket_options(option)
    ticket = db.query_ticket(id)
    comments = db.query_comments(id)
    form = CommentForm(request.form)

    if request.method == 'POST':
        comment = request.form['comment']
        db.insert_comment(id, 'test.user', comment)
        return redirect(url_for('ticket', id=id))
    
    if form.validate(): 
        flash('Comment submitted')
    else:
        flash("Failed")

    return render_template("ticket.html", option=option, tickets=tickets, ticket=ticket, comments=comments, form=form)



# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))