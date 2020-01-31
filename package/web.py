import os
import time
import json
from flask import Flask, render_template, Response, redirect, url_for, request, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField
from datetime import datetime
import modules.database as db
from modules.assorted import convertRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class CommentForm(Form):
    comment = TextAreaField('Comment:')
    submitComment = SubmitField('submit')

class TicketForm(Form):
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    category = SelectField('Category', choices=[('Ticket','Ticket'),('Project','Project'),('WishList','WishList')])
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    submitTicket = SubmitField('submit')

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
    ticketForm = TicketForm(request.form)

    if ticketForm.submitTicket.data and ticketForm.validate():
        subject = ticketForm.subject.data
        body = ticketForm.body.data
        priority = ticketForm.priority.data
        category = ticketForm.category.data
        status = ticketForm.status.data
        db.insert_ticket(subject,body,priority, created_by, status, category)
        result = db.query_ticket_subject(subject)
        return redirect(url_for('ticket', option=option, id=result.id))

    return render_template("index.html", tickets=tickets, ticketForm=ticketForm)

@app.route("/ticket/<option>", methods=['GET','POST'])
def tickets(option):
    tickets = ticket_options(option)
    ticketForm = TicketForm(request.form)

    if ticketForm.submitTicket.data and ticketForm.validate():
        subject = ticketForm.subject.data
        body = ticketForm.body.data
        priority = ticketForm.priority.data
        category = ticketForm.category.data
        status = ticketForm.status.data
        db.insert_ticket(subject,body,priority, created_by, status, category)
        result = db.query_ticket_subject(subject)
        return redirect(url_for('ticket', option=option, id=result.id))
    


    return render_template("tickets.html", option=option, tickets=tickets, ticketForm=ticketForm)


@app.route("/ticket/<option>/<id>", methods=['GET','POST'])
def ticket(option, id):
    tickets = ticket_options(option)
    ticket = db.query_ticket(id)
    comments = db.query_comments(id)
    commentForm = CommentForm(request.form)
    ticketForm = TicketForm(request.form)
    ticketUpdateForm = TicketForm(request.form)

    if ticketForm.submitTicket.data and ticketForm.validate():
        subject = ticketForm.subject.data
        body = ticketForm.body.data
        priority = ticketForm.priority.data
        category = ticketForm.category.data
        status = ticketForm.status.data
        db.insert_ticket(subject,body,priority, created_by, status, category)
        result = db.query_ticket_subject(subject)
        return redirect(url_for('ticket', option=option, id=result.id))

    if ticketUpdateForm.submitTicket.data and ticketUpdateForm.validate():
        subject = ticketUpdateForm.subject.data
        body = ticketUpdateForm.body.data
        priority = ticketUpdateForm.priority.data
        category = ticketUpdateForm.category.data
        status = ticketUpdateForm.status.data
        db.update_ticket(subject,body,priority, created_by, status, category)
        return redirect(url_for('ticket', option=option, id=id))
    
    if commentForm.submitComment.data and commentForm.validate():
        comment = commentForm.comment.data
        db.insert_comment(id, 'test.user', comment)
        return redirect(url_for('ticket', option=option, id=id))
 

    return render_template("ticket.html", option=option, tickets=tickets, ticket=ticket, comments=comments, commentForm=commentForm, ticketForm=ticketForm)

@app.route("/api/<query>")
def api(id, query):
    allowed = ['ticket','status','subject','body','action','priority']
    actions = ['update_ticket','insert_ticket']
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)
    #Process request
    if len(set(requestList).difference(allowed)) > 0:
        result = {"result": 1, "description": "failure", "message": "failed"}
        #(str(set(requestList).difference(allowed)) + f'\nProvided:{requestList}\nAllowed:{allowed}')
    else:
        if requestData.get('action') == 'update_ticket':
            query = db.query_ticket(requestData['ticket'])
            # TODO make optional
            result = db.update_ticket(
                requestData['ticket'],
                query.status,
                requestData['subject'],
                requestData['body'],
                query.priority,
                query.created_by,
                query.assigned,
                query.category,
                query.due_by)
        else: 
            result = {"result": 1, "description": "failure", "message": 'Messed up'}
    result = json.dumps(result)
    return result

#action=update_ticket&ticket=1&subject='API test'&body='This is a test of the API'

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))