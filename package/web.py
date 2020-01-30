import os
import time
from flask import Flask, render_template, Response, redirect, url_for, request, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from datetime import datetime
import modules.database as db

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class CommentForm(Form):
    comment = TextAreaField('Comment:')

@app.route("/")
def home():
    tickets = db.query_tickets_all()

    return render_template("tickets.html", tickets=tickets)

@app.route("/tickets_open")
def tickets_open():
    tickets = db.query_tickets_open()

    return render_template("tickets.html", tickets=tickets)


@app.route("/ticket/<id>", methods=['GET','POST'])
def ticket(id):
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
        flash("Couldn't submit")

    return render_template("ticket.html", ticket=ticket, comments=comments, form=form)



# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))