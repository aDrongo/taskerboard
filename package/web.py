import os
import re
import csv
import time
import json
import hashlib
import requests
import logging
import logging.handlers
from datetime import datetime


#import flaskext.mail as Mail
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask import Flask, render_template, Response, redirect, url_for, request, flash, abort, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField
from imapclient import IMAPClient
import pyzmail

import modules.database as Db
import modules.forms as Forms
from modules.assorted import convertRequest, Load_Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.handlers.RotatingFileHandler("errors.log", maxBytes=1000000, backupCount=3)])
logging.info('Running web.py')

#config = Load_Config()

# Start application
app = Flask(__name__)

# Connect to DB
db = Db.Database('app.db')
#if config.get('mail', None):
#    mail = Mail.Mail(app)

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route("/settings", methods=['GET','POST'])
@login_required
def settings():
    """Manage Settings"""
    users=None
    users = [user for user in Db.query_users(db)]

    userInsertForm = Forms.UserInsertForm(request.form)
    userUpdateForm = Forms.UserUpdateForm(request.form)
    userUpdateForm.username.choices = [(user.username, user.username) for user in users]

    # Download Form


    # Import Form
    importDataForm = Forms.ImportDataForm()

    if importDataForm.validate_on_submit():
        filepath = os.getcwd() + "/upload"
        importDataForm.file.data.save(filepath)
        with open(filepath) as file:
            data = json.load(file)
        os.remove(filepath)

        for ticket in data:
            tags = ''
            for tag in ticket.get('tags'):
                tag = tag.get("body")
                tags = tags + f',{tag}'
            tags = tags[1:]
            assigned = ''
            for user in ticket.get('assigned'):
                user = user.get("username")
                assigned = assigned + f'{user},'
            Db.insert_ticket(db,
                subject=ticket['subject'],
                body=ticket.get('body', None),
                status=ticket.get('status', None),
                priority=ticket.get('priority', None),
                tags=tags,
                created_by=ticket.get('created_by', None),
                assigned=assigned,
                due_by=ticket.get('due_by', None)
                )

    # Insert Ticket form
    if userInsertForm.submitInsertUser.data and userInsertForm.validate():
        result = Forms.user_insert_form(db, userInsertForm)
        if result == True:
            flash('Success!')
        else:
            flash('Failed!')
        return redirect(url_for('settings'))

    # Update Ticket form
    if userUpdateForm.submitUpdateUser.data and userUpdateForm.validate():
        result = Forms.user_update_form(db, userUpdateForm)
        if result == True:
            flash('Success!')
        else:
            flash('Failed!')
        return redirect(url_for('settings'))

    return render_template('settings.html', users=users, userInsertForm=userInsertForm, userUpdateForm=userUpdateForm, importDataForm=importDataForm)

@app.route("/", methods=['GET','POST'])
@login_required
def home():
    """Redirect to home_query"""
    return redirect('/display=index')

@app.route("/<query>", methods=['GET','POST'])
@login_required
def home_query(query):
    """Main webpage, dynamically generate from url string"""
    # Split data
    requestData = convertRequest(query)
    # Get List of Keys
    requestList = list(requestData)

    # Pass variables as None if nothing set for them
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
    queries['filter'] = re.sub('&?status=\w+|&?search=\w+', '', query)
    queries['order'] = re.sub('&?order=\w+', '', query)
    queries['sort'] = re.sub('&?sort=\w+', '', query)
    queries['search'] = re.sub('&?search=\w', '', query)
    if 'sort' in requestList:
        queries['sorted'] = requestData.get('sort')
    assigned = re.sub('&?assigned=\w+\.?\w+', '', query) + f'&assigned={current_user.id}'
    if 'assigned' in requestList:
        noassigned = re.sub('&?assigned=\w+\.?\w+', '', query)


    # Get Tickets based on Query
    tickets = Db.query_tickets(db,
            status=requestData.get('status', None),
            tags=requestData.get('tags', None),
            assigned=requestData.get('assigned', None),
            order=requestData.get('order', None),
            subject=requestData.get('subject', None),
            search=requestData.get('search', None),
            sort=requestData.get('sort',None))

    # Data to pass into templates
    users = [(user.username, user.username) for user in Db.query_users(db)]
    tags = [tag for tag in Db.query_tags(db)]
    statuses = [status.name for status in Db.Status]
    priorities = [priority.name for priority in Db.Priority]

    # Convert tags list to string
    def tags_string(list_items):
        """Convert Tags List to String with comma's"""
        string = ""
        for item in list_items:
            string = string + "," + item.body
        return string[1:]

    # Get Display based on Query
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

        # Submit Update Ticket form
        if ticketUpdateForm.submitUpdateTicket.data and ticketUpdateForm.validate():
            result = Forms.ticket_update_form(db, ticketUpdateForm, id)
            return redirect(url_for('home_query', query=query))
    
        # Submit Comment form
        if commentForm.submitComment.data and commentForm.validate():
            comment = commentForm.comment.data
            Db.insert_comment(db, id, current_user.id, comment)
            return redirect(url_for('home_query', query=query))

    # Initialize insert ticket form
    ticketInsertForm = Forms.TicketInsertForm(request.form)
    ticketInsertForm.assigned.choices = users
    ticketInsertForm.assigned.choices.append(('None', 'None'))

    # Submit Insert Ticket Form
    if ticketInsertForm.submitInsertTicket.data and ticketInsertForm.validate():
        result = Forms.ticket_insert_form(db, ticketInsertForm, current_user.id)
        if requestData.get('display', None):
            re_display = re.sub('&?display=\w+', '', query) + '&display=board'
        return redirect(url_for('home_query', query=(re_display + f'&ticket={result.id}')))
    
    # Intialize search form
    searchForm = Forms.TicketSearchForm(request.form)

    # Submit Search Form submission
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
        elif requestData.get('action') == 'insert_tags':
            result = Db.insert_tags(db,
                tags=requestData.get('tags', None)
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
            result = Db.convert_to_dict(db, result)
            result = json.dumps(result)
        return result

@app.route("/mail/receive")
def mail_receieve():
    mail_username = os.environ['mail_user']
    mail_password = os.environ['mail_pass']
    mail_server = os.environ['mail_server']
    mail_connection = IMAPClient(mail_server, use_uid=True)

    with mail_connection as c:
        c.login(mail_username,mail_password)
        c.select_folder('INBOX', readonly=True)
        #messages = server.sort('ARRIVAL')
        UIDs = c.search(['ALL'])
        print(UIDs)
        messages = c.fetch([UIDs[-1]], ['Body[]', 'FLAGS'])
        message = messages[list(messages)[0]][b'BODY[]']
        pyzmessage = pyzmail.PyzMessage.factory(message)
        from_address = pyzmessage.get_address('from')[1]
        from_user = pyzmessage.get_address('from')[0]
        cc = pyzmessage.get_adresses('cc')
        subject = pyzmessage.get_subject()
        body = pyzmessage.html_part.get_payload().decode('UTF-8')
        #body = pyzmessage.text_part.get_payload().decode('UTF-8')

    result = f'{from_address} <br>{from_user} <br>{subject} <br>{body}'
    return result

@app.route("/mail/send/<details>")
def mail_send(details):
    """Send Mail
    MAIL_SERVER : default ‘localhost’
    MAIL_PORT : default 25
    MAIL_USE_TLS : default False
    MAIL_USE_SSL : default False
    MAIL_DEBUG : default app.debug
    MAIL_USERNAME : default None
    MAIL_PASSWORD : default None
    DEFAULT_MAIL_SENDER : default None """
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)

    #msg = Message("String")

    #Recipients
    #msg.recipients = ['example@test.com']
    #msg.add_recipient('example2@test.com)

    #Body
    #msg.body = "testing"
    #msg.html = "<b>testing</b>"

    #Attachments
    #with app.open_resource("image.png") as fp:
    #msg.attach("image.png", "image/png", fp.read())

    #Send
    #mail.send(msg)

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))