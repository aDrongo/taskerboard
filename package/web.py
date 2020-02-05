import os
import time
import json
from flask_login import LoginManager, login_required, login_user
from flask import Flask, render_template, Response, redirect, url_for, request, flash, abort
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField
from datetime import datetime
import modules.database as db
from modules.assorted import convertRequest


app = Flask(__name__)
#TODO Make secret for Production
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(Form):
    loginemail = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    loginpassword = PasswordField('password', validators=[validators.DataRequired(message="Password field is required")])
    submit = SubmitField('submit', [validators.DataRequired()])

class CommentForm(Form):
    """WTForm for Comments"""
    comment = TextAreaField('Comment:')
    submitComment = SubmitField('submit')

class TicketInsertForm(Form):
    """WTForm for Inserting a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    category = SelectField('Category', choices=[('ticket','Ticket'),('project','Project'),('wishList','WishList')])
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    submitInsertTicket = SubmitField('submit')

class TicketUpdateForm(Form):
    """WTForm for Updating a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    category = SelectField('Category', choices=[('ticket','Ticket'),('project','Project'),('wishList','WishList')])
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    submitUpdateTicket = SubmitField('submit')

def ticket_insert_form(Form, db):
    """Insert a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = db.Priority[f'{Form.priority.data}'].value
    category = Form.category.data
    status = db.Status[f'{Form.status.data}'].value
    created_by = 'test.user'
    db.insert_ticket(subject,body,priority, created_by, status, category)
    result = db.query_ticket_subject(subject)
    return result

def ticket_update_form(Form, db, id):
    """"Update a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = db.Priority[f'{Form.priority.data}'].value
    category = Form.category.data
    status = db.Status[f'{Form.status.data}'].value
    assigned = None
    due_by = None
    created_by = 'test.user'
    result = db.update_ticket(id, status, subject, body, priority, created_by, assigned, category, due_by)
    return result

def tickets_query(option=None):
    """Return tickets query based on option"""
    tickets = db.query_tickets(option,'ticket','updated_at')
    return tickets

@app.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm(request.form)
    if loginForm.submit.data and loginForm.validate():
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('/board')
        if not is_safe_url(next):
            return abort(400)
        return redirect(flask.url_for('home'))
    return render_template('login.html', loginForm=loginForm)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/", methods=['GET','POST'])
def home():
    tickets = tickets_query()
    projects = db.query_tickets(None,'project')
    ticketInsertForm = TicketInsertForm(request.form)
    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        subject = ticketInsertForm.subject.data
        body = ticketInsertForm.body.data
        priority = db.Priority[f'{ticketInsertForm.priority.data}'].value
        category = ticketInsertForm.category.data
        status = db.Status[f'{ticketInsertForm.status.data}'].value
        created_by = 'test.user'
        db.insert_ticket(subject,body,priority, created_by, status, category)
        result = db.query_ticket_subject(subject)
        return redirect(url_for('board', id=result.id))

    
    return render_template("index.html", tickets=tickets, ticketInsertForm=ticketInsertForm, projects=projects)

@app.route("/test", methods=['GET','POST'])
def test():
    return render_template('test.html')

@login_required
@app.route("/board", methods=['GET','POST'])
def boards():
    tickets = db.query_tickets(None,'project')
    ticketInsertForm = TicketInsertForm(request.form)

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = ticket_insert_form(ticketInsertForm, db)
        return redirect(url_for('board', id=result.id))

    return render_template("project.html", tickets=tickets, ticketInsertForm=ticketInsertForm)

@app.route("/board/<id>", methods=['GET','POST'])
def board(id):
    tickets = db.query_tickets(None,'project')
    ticket = db.query_ticket(id)
    comments = db.query_comments(id,'created_at')
    commentForm = CommentForm(request.form)
    ticketInsertForm = TicketInsertForm(request.form)
    ticketUpdateForm = TicketUpdateForm(request.form)

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = ticket_insert_form(ticketInsertForm, db)
        return redirect(url_for('board', id=result.id))

    if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
        result = ticket_update_form(ticketUpdateForm, db, ticket)
        return redirect(url_for('board', id=id))
    
    if commentForm.submitComment.data and commentForm.validate():
        comment = commentForm.comment.data
        db.insert_comment(id, 'test.user', comment)
        return redirect(url_for('board', id=id))

    return render_template("project.html", id=int(id), tickets=tickets, ticket=ticket, comments=comments, commentForm=commentForm, ticketUpdateForm=ticketUpdateForm, ticketInsertForm=ticketInsertForm)


@app.route("/ticket/<option>", methods=['GET','POST'])
def tickets(option):
    allowed = ['open','working','waiting','closed','all']
    if option not in allowed:
        tickets = tickets_query()
    else:
        tickets = tickets_query(option)
    ticketInsertForm = TicketInsertForm(request.form)

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = ticket_insert_form(ticketInsertForm, db)
        return redirect(url_for('ticket', option=option, id=result.id))

    return render_template("ticket.html", option=option, tickets=tickets, ticketInsertForm=ticketInsertForm)


@app.route("/ticket/<option>/<id>", methods=['GET','POST'])
def ticket(option, id):
    allowed = ['open','working','waiting','closed','all']
    if option not in allowed:
        tickets = tickets_query()
    else:
        tickets = tickets_query(option)
    ticket = db.query_ticket(id)
    comments = db.query_comments(id,'created_at')
    commentForm = CommentForm(request.form)
    ticketInsertForm = TicketInsertForm(request.form)
    ticketUpdateForm = TicketUpdateForm(request.form)

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = ticket_insert_form(ticketInsertForm, db)
        return redirect(url_for('ticket', option=option, id=result.id))

    if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
        result = ticket_update_form(ticketUpdateForm, db, id)
        return redirect(url_for('ticket', option=option, id=id))
    
    if commentForm.submitComment.data and commentForm.validate():
        comment = commentForm.comment.data
        db.insert_comment(id, 'test.user', comment)
        return redirect(url_for('ticket', option=option, id=id))

    return render_template("ticket.html", id=int(id), option=option, tickets=tickets, ticket=ticket, comments=comments, commentForm=commentForm, ticketUpdateForm=ticketUpdateForm, ticketInsertForm=ticketInsertForm)

@app.route("/api/<query>")
def api(query):
    print('Query')
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
            print('update_ticket')
            status = requestData['status']
            status = db.Status[f'{status}'].value
            query = db.query_ticket(requestData['ticket'])
            # TODO make optional
            result = db.update_ticket(
                requestData['ticket'],
                status,
                requestData['subject'],
                requestData['body'],
                query.priority,
                query.created_by,
                query.assigned,
                query.category,
                query.due_by)
        elif requestData.get('action') == 'update_ticket_status':
            print('update_ticket_status')
            status = requestData['status']
            status = db.Status[f'{status}'].value
            result = db.update_ticket_status(
                requestData['ticket'],
                status
            )
        else: 
            result = {"result": 1, "description": "failure", "message": 'Messed up'}
    result = json.dumps(result)
    return result

#action=update_ticket&ticket=1&subject='API test'&body='This is a test of the API'&status=Working

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))