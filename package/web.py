import os
import re
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

    return redirect('/display=index')

@app.route("/<query>", methods=['GET','POST'])
@login_required
def home_query(query):
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)

    #Get Tickets based on Query
    tickets = Db.query_tickets(
            status=requestData.get('status', None),
            tags=requestData.get('tags', None),
            assigned=requestData.get('assigned', None),
            order=requestData.get('order', None))
    
    id = None
    ticket = None
    comments = None
    commentForm = None
    ticketUpdateForm = None
    boards = None

    if 'ticket' in requestList:
        id = requestData['ticket']
        ticket = Db.query_tickets(id=id)

    #Get Display based on Query
    if requestData.get('display') == 'board':
        display = 'board.html'
    elif requestData.get('display') == 'list':
        display = 'list.html'
    elif requestData.get('display') == 'index':
        display = 'index.html'
        boards = Db.query_tickets(assigned=current_user.id)
    else:
        display = 'list.html'
    
    #Get Tags and convert list to a string
    if 'tags' in requestList:
        seperator = ', '
        tags= seperator.join([string.to_string() for string in ticket.tags])

    #Forms
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    if 'ticket' in requestList:
        comments = Db.query_comments(requestData['ticket'],'created_at')
        commentForm = Forms.CommentForm(request.form)
        ticketUpdateForm = Forms.TicketUpdateForm(request.form)

        if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
            result = Forms.ticket_update_form(ticketUpdateForm, Db, id)
            return redirect(url_for('ticket', option=option, id=id))
    
        if commentForm.submitComment.data and commentForm.validate():
            comment = commentForm.comment.data
            Db.insert_comment(id, current_user.id, comment)
            return redirect(url_for('ticket', option=option, id=id))

    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(ticketInsertForm, Db, current_user.id)
        return redirect(url_for('ticket', option=option, id=result.id))


    re_query = re.sub('ticket=\d+', '', query)
    re_filter = re.sub('&?status=\w+', '', query)
    re_order = re.sub('&?order=\w+', '', query)

    return render_template(display, order=re_order, query=re_query, filter=re_filter, id=id, boards=boards, tickets=tickets, ticket=ticket, ticketInsertForm=ticketInsertForm, ticketUpdateForm=ticketUpdateForm, commentForm=commentForm, comments=comments)


@app.route("/api/<query>")
def api(query):
    print('Query')
    allowed = ['ticket','status','subject','body','action','priority','assigned','tags']
    actions = ['update_ticket','insert_ticket','update_ticket_status','query_ticket','query_tickets']
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