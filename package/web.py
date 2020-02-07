import os
import time
import json
import hashlib
from datetime import datetime

from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from flask import Flask, render_template, Response, redirect, url_for, request, flash, abort, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField

import modules.database as Db
import modules.forms as Forms
from modules.assorted import convertRequest


app = Flask(__name__)
#TODO Make secret for Production
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
login_manager = LoginManager()
login_manager.init_app(app)

class LoginUser(UserMixin):
    """User for Flask Session"""
    import modules.database as Db
    import hashlib
    #is_authenticated(boolean)
    #is_active(boolean)
    #is_anonymous(boolean)
    #get_id(unicode)

    def __init__(self, username):
        """Retrieve user from Db"""
        self.auth = None
        user = Db.get_user(username)
        if user is not None:
            self.id = user.username
            self.password = user.password_hash
        else:
            self.auth = False
            return None
    
    def check_password(self, password):
        """Compare password hashes"""
        hash = hashlib.md5()
        password_enc = password.encode()
        hash.update(password_enc)
        hash = hash.hexdigest()
        if hash == self.password:
            return True
        else:
            return False

@login_manager.user_loader
def load_user(id):
    """Checks user for login_required"""
    return LoginUser(id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Logged in successfully.')
        return redirect(url_for('home'))
    loginForm = Forms.LoginForm(request.form)
    if loginForm.submitLogin.data and loginForm.validate():
        user = LoginUser(loginForm.username.data)
        print('---')
        print(dir(user))
        print('---')
        if user.auth is False:
            flash('Failed to Login, bad username')
            return redirect(url_for('login'))
        elif user.check_password(loginForm.password.data) is None:
            flash('Failed to Login, bad password')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=loginForm.remember_me.data)
            return redirect(url_for('home'))
    return render_template('login.html', loginForm=loginForm, current_user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('login'))

@app.route("/", methods=['GET','POST'])
@login_required
def home():
    tickets = Db.query_tickets()
    projects = Db.query_tickets()
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        subject = ticketInsertForm.subject.data
        body = ticketInsertForm.body.data
        priority = Db.Priority[f'{ticketInsertForm.priority.data}'].value
        tags = ticketInsertForm.tags.data
        status = Db.Status[f'{ticketInsertForm.status.data}'].value
        created_by = str(current_user.id)
        Db.insert_ticket(subject,body,priority, created_by, status, tags)
        result = Db.query_ticket_subject(subject)
        return redirect(url_for('index'))
    
    return render_template("index.html", tickets=tickets, ticketInsertForm=ticketInsertForm, projects=projects, current_user=current_user)

@app.route("/test", methods=['GET','POST'])
@login_required
def test():
    return render_template('test.html')

@app.route("/board", methods=['GET','POST'])
@login_required
def boards():
    tickets = Db.query_tickets()
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(ticketInsertForm, Db)
        return redirect(url_for('board', id=result.id))

    return render_template("project.html", tickets=tickets, ticketInsertForm=ticketInsertForm, current_user=current_user)

@app.route("/board/<id>", methods=['GET','POST'])
@login_required
def board(id):
    tickets = Db.query_tickets()
    ticket = Db.query_ticket(id)
    comments = Db.query_comments(id,'created_at')
    commentForm = Forms.CommentForm(request.form)
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    ticketUpdateForm = Forms.TicketUpdateForm(request.form)
    seperator = ', '
    tags= seperator.join([string.to_string() for string in ticket.tags])

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(ticketInsertForm, Db, current_user.id)
        return redirect(url_for('board', id=result.id))

    if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
        result = Forms.ticket_update_form(ticketUpdateForm, Db, id)
        return redirect(url_for('board', id=id))
    
    if commentForm.submitComment.data and commentForm.validate():
        comment = commentForm.comment.data
        Db.insert_comment(id, 'test.user', comment)
        return redirect(url_for('board', id=id))

    return render_template("project.html", id=int(id), tags=tags, tickets=tickets, ticket=ticket, comments=comments, commentForm=commentForm, ticketUpdateForm=ticketUpdateForm, ticketInsertForm=ticketInsertForm, current_user=current_user)


@app.route("/ticket/<option>", methods=['GET','POST'])
@login_required
def tickets(option):
    allowed = ['open','working','waiting','closed','all']
    if option not in allowed:
        tickets = Db.query_tickets()
    else:
        tickets = Db.query_tickets(status=f'{option}')
    ticketInsertForm = Forms.TicketInsertForm(request.form)

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(ticketInsertForm, Db, current_user.id)
        return redirect(url_for('ticket', option=option, id=result.id))

    return render_template("list.html", option=option, tickets=tickets, ticketInsertForm=ticketInsertForm, current_user=current_user)


@app.route("/ticket/<option>/<id>", methods=['GET','POST'])
@login_required
def ticket(option, id):
    allowed = ['open','working','waiting','closed','all']
    if option not in allowed:
        tickets = Db.query_tickets()
    else:
        tickets = Db.query_tickets(status=option)
    ticket = Db.query_ticket(id)
    comments = Db.query_comments(id,'created_at')
    commentForm = Forms.CommentForm(request.form)
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    ticketUpdateForm = Forms.TicketUpdateForm(request.form)
    seperator = ', '
    tags= seperator.join([string.to_string() for string in ticket.tags])

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(ticketInsertForm, Db, current_user.id)
        return redirect(url_for('ticket', option=option, id=result.id))

    if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
        result = Forms.ticket_update_form(ticketUpdateForm, Db, id)
        return redirect(url_for('ticket', option=option, id=id))
    
    if commentForm.submitComment.data and commentForm.validate():
        comment = commentForm.comment.data
        Db.insert_comment(id, current_user.id, comment)
        return redirect(url_for('ticket', option=option, id=id))

    return render_template("list.html", id=int(id), tags=tags, option=option, tickets=tickets, ticket=ticket, comments=comments, commentForm=commentForm, ticketUpdateForm=ticketUpdateForm, ticketInsertForm=ticketInsertForm, current_user=current_user)

@app.route("/api/<query>")
def api(query):
    print('Query')
    allowed = ['ticket','status','subject','body','action','priority','assigned','tags']
    actions = ['update_ticket','insert_ticket','update_ticket_status','query_ticket','query_tickets','query_projects']
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
            result = Db.update_ticket(
                id=requestData['ticket'],
                subject=requestData['subject'],
                body=requestData.get('body', None),
                status=requestData.get('status', None),
                priority=requestData.get('priority', None),
                tags=requestData.get('tags', None),
                created_by=requestData.get('created_by', None),
                assigned=requestData.get('assigned', None),
                due_by=requestData.get('due_by', None))
        elif requestData.get('action') == 'update_ticket_status':
            status = requestData['status']
            result = Db.update_ticket_status(
                requestData['ticket'],
                status
            )
        elif requestData.get('action') == 'insert_ticket':
            result = Db.insert_ticket(
                subject=requestData['subject'],
                body=requestData.get('body', None),
                status=requestData.get('status', None),
                priority=requestData.get('priority', None),
                tags=requestData.get('tags', None),
                created_by=requestData.get('created_by', None),
                assigned=requestData.get('assigned', None),
                due_by=requestData.get('due_by', None)
                )
        elif requestData.get('action') == 'query_tickets':
            if 'assigned' in requestList:
                assigned = requestData['assigned']
                result = Db.query_user_tickets(assigned)
            elif 'tags' in requestList:
                tags = requestData['tags']
                array = tags.split(',')
                result = Db.query_tickets_tags(array)
            else:
                Db.query_tickets
        else: 
            result = {"result": 1, "description": "failure", "message": 'Messed up'}
    try:
        result = json.dumps(result)
    except:
        result = Db.convert_to_dict(result)
        result = json.dumps(result)
    return result

#action=query_tickets&tags=tick
#action=update_ticket&ticket=1&subject='API test'&body='This is a test of the API'&status=Working

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))