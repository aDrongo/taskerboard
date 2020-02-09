import os
import re
import time
import json
import hashlib
import logging
import logging.handlers
from datetime import datetime

from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask import Flask, render_template, Response, redirect, url_for, request, flash, abort, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField

import modules.database as Db
import modules.forms as Forms
from modules.assorted import convertRequest

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.handlers.RotatingFileHandler("errors.log", maxBytes=1000000, backupCount=3)])
logging.info('Running web.py')

# Start application
app = Flask(__name__)

# Connect to DB
db = Db.Database('app.db')

#TODO Make secret for Production
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

@login_manager.user_loader
def load_user(id):
    """Checks user for login_required"""
    return Forms.LoginUser(db, id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Allows User to login"""
    if current_user.is_authenticated and len(current_user.id) > 0:
        flash('Logged in successfully.')
        return redirect(url_for('home'))
    loginForm = Forms.LoginForm(request.form)
    if loginForm.submitLogin.data and loginForm.validate():
        user = Forms.LoginUser(db, loginForm.username.data)
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
    """Logs out the User"""
    logout_user()
    flash('Logged Out')
    return redirect(url_for('login'))

@app.route("/users", methods=['GET','POST'])
@login_required
def users():
    """Manage Users"""
    users=None
    users = [user for user in Db.get_users(db)]

    userInsertForm = Forms.UserInsertForm(request.form)
    userUpdateForm = Forms.UserUpdateForm(request.form)
    userUpdateForm.username.choices = [(user.username, user.username) for user in Db.get_users(db)]

    # Insert Ticket form
    if userInsertForm.submitInsertUser.data and userInsertForm.validate():
        result = Forms.user_insert_form(db, userInsertForm)
        if result == True:
            flash('Success!')
        else:
            flash('Failed!')
        return redirect(url_for('users'))

    # Update Ticket form
    if userUpdateForm.submitUpdateUser.data and userUpdateForm.validate():
        result = Forms.user_update_form(db, userUpdateForm)
        if result == True:
            flash('Success!')
        else:
            flash('Failed!')
        return redirect(url_for('users'))

    return render_template('users.html', users=users, userInsertForm=userInsertForm, userUpdateForm=userUpdateForm)

@app.route("/", methods=['GET','POST'])
@login_required
def home():
    """Redirect to home_query"""
    return redirect('/display=index')

@app.route("/<query>", methods=['GET','POST'])
@login_required
def home_query(query):
    """Main webpage, dynamically generate from url string"""
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)

    #Pass variables as None if nothing set for them
    id = None
    ticket = None
    comments = None
    commentForm = None
    ticketUpdateForm = None
    boards = None
    noassigned = None

    # Format query for replacement text insertion
    queries = {}
    queries['query'] = query
    queries['ticket'] = re.sub('&?ticket=\d+', '', query)
    queries['filter'] = re.sub('&?status=\w+|&?search=\w+|&?assigned=\w+.?\w+', '', query)
    queries['order'] = re.sub('&?order=\w+', '', query)
    queries['sort'] = re.sub('&?sort=\w+', '', query)
    queries['search'] = re.sub('&?search=\w', '', query)
    if 'sort' in requestList:
        queries['sorted'] = requestData.get('sort')
    assigned = re.sub('&?assigned=\w+\.?\w+', '', query) + f'&assigned={current_user.id}'
    if 'assigned' in requestList:
        noassigned = re.sub('&?assigned=\w+\.?\w+', '', query)

    #Get Tickets based on Query
    tickets = Db.query_tickets(db,
            status=requestData.get('status', None),
            tags=requestData.get('tags', None),
            assigned=requestData.get('assigned', None),
            order=requestData.get('order', None),
            subject=requestData.get('subject', None),
            search=requestData.get('search', None),
            sort=requestData.get('sort',None))

    #Data to pass into templates
    users = [(user.username, user.username) for user in Db.get_users(db)]
    tags = [tag for tag in Db.query_tags(db)]
    statuses = [status.name for status in Db.Status]
    priorities = [priority.name for priority in Db.Priority]

    #Convert tags list to string
    def tags_string(list_items):
        """Convert Tags List to String with comma's"""
        string = ""
        for item in list_items:
            string = string + "," + item.body
        return string[1:]

    #Get Display based on Query
    if requestData.get('display') == 'board':
        display = 'board.html'
    elif requestData.get('display') == 'list':
        display = 'list.html'
    elif requestData.get('display') == 'index':
        display = 'index.html'
        #if index, get assigned tickets for current user for boards display
        boards = Db.query_tickets(db, assigned=current_user.id, order=requestData.get('order', None))
    else:
        display = 'list.html'

    # If specific ticket identified, retrieve it
    if 'ticket' in requestList:
        id = requestData['ticket']
        ticket = Db.query_tickets(db, id=id)
        comments = Db.query_comments(db, requestData['ticket'],'created_at')

        # Initialize forms
        commentForm = Forms.CommentForm(request.form)
        ticketUpdateForm = Forms.TicketUpdateForm(request.form)
        ticketUpdateForm.assigned.choices = users
        ticketUpdateForm.assigned.choices.append(('None', 'None'))

        # Update Ticket form
        if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
            result = Forms.ticket_update_form(db, ticketUpdateForm, id)
            return redirect(url_for('home_query', query=query))
    
        # Comment form
        if commentForm.submitComment.data and commentForm.validate():
            comment = commentForm.comment.data
            Db.insert_comment(db, id, current_user.id, comment)
            return redirect(url_for('home_query', query=query))

    # Initialize insert ticket form
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    ticketInsertForm.assigned.choices = users
    ticketInsertForm.assigned.choices.append(('None', 'None'))

    # Insert Ticket Form
    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(db, ticketInsertForm, current_user.id)
        if requestData.get('display', None):
            re_display = re.sub('&?display=\w+', '', query) + '&display=board'
        return redirect(url_for('home_query', query=(re_display + f'&ticket={result.id}')))
    
    # Intialize search form
    searchForm = Forms.TicketSearchForm(request.form)

    # Search Form submission
    if searchForm.submitSearch and searchForm.validate():
        search = searchForm.search.data
        return redirect(url_for('home_query', query=(queries['filter'] + f"&search={search}")))
    return render_template(display, tags_string=tags_string, statuses=statuses, priorities=priorities, users=users, tags=tags, queries=queries, 
                            id=id, searchForm=searchForm, assigned=assigned, noassigned=noassigned, boards=boards, tickets=tickets, ticket=ticket,
                            ticketInsertForm=ticketInsertForm, ticketUpdateForm=ticketUpdateForm, commentForm=commentForm, comments=comments)

@app.route("/api/<query>")
def api(query):
    """API interface"""
    allowed = ['ticket','status','subject','body','action','priority','assigned','tags']
    actions = ['update_ticket','insert_ticket','query_ticket','query_tickets']
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)
    #Process request
    if len(set(requestList).difference(allowed)) > 0:
        result = {"result": 1, "description": "failure", "message": "failed"}
        #(str(set(requestList).difference(allowed)) + f'\nProvided:{requestList}\nAllowed:{allowed}')
    else:
        print(query)
        if requestData.get('action') == 'update_ticket':
            result = Db.update_ticket(db,
                id=requestData['ticket'],
                subject=requestData.get('subject', None),
                body=requestData.get('body', None),
                status=requestData.get('status', None),
                priority=requestData.get('priority', None),
                tags=requestData.get('tags', None),
                created_by=requestData.get('created_by', None),
                assigned=requestData.get('assigned', None),
                due_by=requestData.get('due_by', None))
        elif requestData.get('action') == 'insert_ticket':
            result = Db.insert_ticket(db,
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
            result = Db.query_tickets(db,
                id=requestData.get('ticket', None),
                subject=requestData.get('subject', None),
                status=requestData.get('status', None),
                tags=requestData.get('tags', None),
                assigned=requestData.get('assigned', None),
                order=requestData.get('order', None)
                )
        else: 
            result = {"result": 1, "description": "failure", "message": 'Messed up'}
    try:
        result = json.dumps(result)
    except:
        result = Db.convert_to_dict(result)
        result = json.dumps(result)
    return result

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))