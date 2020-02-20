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

import pyzmail
import flask_mail as FlaskMail
from imapclient import IMAPClient
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask import Flask, render_template, Response, redirect, url_for, request, flash, abort, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField
from wtforms.fields.html5 import EmailField
from apscheduler.schedulers.background import BackgroundScheduler

import modules.database as Db
import modules.forms as Forms
import modules.mail as Mail
from modules.assorted import convertRequest, Load_Config, query_args, tags_string, html_email

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.handlers.RotatingFileHandler("errors.log", maxBytes=1000000, backupCount=3)])
logging.info('Running web.py')

config = Load_Config('config')

# Start application
app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a' #TODO Make secret for Production

# Connect to DB
db = Db.Database('app.db')

# Load Mail client if configured
if config.get('mail_server', None):
    app.config['MAIL_SERVER']=config.get('mail_server')
    app.config['MAIL_PORT'] =config.get('mail_port')
    app.config['MAIL_USERNAME'] = config.get('mail_username')
    app.config['MAIL_PASSWORD'] = config.get('mail_password')
    app.config['MAIL_DEBUG'] = False
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    flask_mail = FlaskMail.Mail(app)

def flash_result(result):
    if result == True:
        return flash('Success!')
    else:
        return flash('Failed!')

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

@app.route("/settings", methods=['GET','POST'])
@login_required
def settings():
    """Manage Settings"""
    users=None
    users = [user for user in Db.query_users(db)]

    #Load Forms
    userForms = Forms.UserForms(db)
    settingsForms = Forms.SettingsForms()

    # Import feature
    if settingsForms.importDataForm.validate_on_submit():
        result = settingsForms.importDataForm.submit(db)

    # Insert User form
    if userForms.userInsertForm.submitInsertUser.data and userForms.userInsertForm.validate():
        result = userForms.userInsertForm.user_insert(db)
        flash_result(result)
        return redirect(url_for('settings'))

    # Update User form
    if userForms.userUpdateForm.submitUpdateUser.data and userForms.userUpdateForm.validate():
        result = userForms.userUpdateForm.user_update(db)
        flash_result(result)
        return redirect(url_for('settings'))

    return render_template('settings.html', users=users, userForms=userForms, settingsForms=settingsForms)

@app.route("/", methods=['GET','POST'])
@login_required
def home():
    """Redirect to home_query"""
    return redirect('/display=index')

@app.route("/<query>", methods=['GET','POST'])
@login_required
def home_query(query):
    """Main webpage, dynamically generate from url string"""
    # Convert query to dictionary
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
    assigned = None

    # Format query for replacement text insertion
    queries = query_args(query, 'query','ticket','status','order','sort','sorted','assigned','search','size','display')
    print(query_args(query, 'status')['status'])
    queries['all'] = query_args(query_args(query, 'search')['search'], 'status')['status']
    if 'assigned' in requestList:
        assigned = True
    else:
        queries['assigned'] = queries['assigned'] + f'&assigned={current_user.id}'
    print(queries)

    # Get Display based on Query
    display = requestData.get('display', 'list') 
    if display in ('board','list','index'):
        display = display + '.html'
    else:
        display = 'list.html'
    
    #if index, get assigned tickets for current user for boards display
    if display == 'index.html':
        boards = Db.query_tickets(db, assigned=current_user.id, order=requestData.get('order', None))

    # Get Tickets based on Query
    size = requestData.get('size','15')
    tickets = Db.query_tickets(db,
            status=requestData.get('status', None),
            tags=requestData.get('tags', None),
            assigned=requestData.get('assigned', None),
            order=requestData.get('order', None),
            subject=requestData.get('subject', None),
            search=requestData.get('search', None),
            sort=requestData.get('sort',None),
            size=size)

    if 'ticket' in requestList:
        id = requestData['ticket']
        ticket = Db.query_tickets(db, id=id)
        comments = Db.query_comments(db, requestData['ticket'],'created_at')
    
    # Data to pass into templates
    users = [(user.username, user.username) for user in Db.query_users(db)]
    tags = [tag for tag in Db.query_tags(db)]
    statuses = Db.get_statuses()
    priorities = Db.get_priorities()

    # Create Forms
    forms = Forms.TicketForms(db, ticket, current_user.id)

    # Submit Insert Ticket Form
    if forms.ticketInsertForm.submitInsertTicket.data and forms.ticketInsertForm.validate():
        result = forms.ticketInsertForm.ticket_insert(db)
        return redirect(url_for('home_query', query=queries['ticket'] + f'&ticket={result.id}'))

    # Submit Search Form submission
    if forms.searchForm.submitSearch and forms.searchForm.validate():
        search = forms.searchForm.search.data
        return redirect(url_for('home_query', query=(queries['search'] + f"&search={search}")))

    if id:
        # Submit Update Ticket form
        if forms.ticketUpdateForm.submitUpdateTicket.data and forms.ticketUpdateForm.validate():
            forms.ticketUpdateForm.ticket_update(db, id)
            return redirect(url_for('home_query', query=query))
    
        # Submit Comment form
        if forms.commentForm.submitComment.data and forms.commentForm.validate():
            forms.commentForm.insert_comment(db, id)
            return redirect(url_for('home_query', query=query))

    return render_template(display, tags_string=tags_string, statuses=statuses, priorities=priorities, users=users, tags=tags, queries=queries, forms=forms,
                            id=id, assigned=assigned, boards=boards, tickets=tickets, ticket=ticket, comments=comments)

@app.route('/logs/')
@login_required
def logs_redirect():
    return redirect ("/logs/all")

@app.route('/logs/<query>', methods=['GET','POST'])
@login_required
def logs(query):
    #Split data
    requestData = convertRequest(query)
    #Get List of Keys
    requestList = list(requestData)

    logs = Db.query_logs(db,
        timestamp = requestData.get('timestamp',None),
        event = requestData.get('event',None),
        table = requestData.get('table',None),
        item_id = requestData.get('item_id',None),
        details = requestData.get('details',None),
        source = requestData.get('source',None),
        trigger = requestData.get('trigger',None))
    
    forms = Forms.LogSearchForm()

    if forms.submitSearch.data:
        search_query = forms.log_search_query()
        return redirect(f"/logs/{search_query}")

    return render_template('logs.html', forms=forms, logs=logs)

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
        elif requestData.get('action') == 'insert_comment':
            result = Db.insert_comment(db,
                ticket=requestData['ticket'],
                body=requestData['body'],
                created_by=requestData['created_by'],
                variety=requestData.get('variety')
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

@app.route("/mail/send", methods=['POST'])
def mail_send():
    """Send Mail using flask-mail with ticket id and recipients"""
    if config.get('mail_server', None) is None:
        abort(400)
    if not request.json or not ('ticket_id' in request.json) or not ('recipients' in request.json):
        abort(400)
    data = json.loads(request.json)
    ticket_id = data['ticket_id']
    subject = data.get('subject', f'#Ticket {ticket_id}')
    recipients = data['recipients'].split(",")
    ticket = Db.query_tickets(db, id=ticket_id)
    comments = Db.query_comments(db, ticket_id)

    #Meta
    sender = config.get('mail_username')
    msg = FlaskMail.Message(subject, sender=sender,recipients=recipients)
    msg.ticket = ticket
    msg.comments = comments

    #Body
    msg.html = html_email(msg)

    #Attachments
    #with app.open_resource("image.png") as fp:
    #msg.attach("image.png", "image/png", fp.read())

    #Send
    result = flask_mail.send(msg)
    return f'{result}'

@app.route("/ticket/<id>")
@login_required
def ticket_html(id):
    result = Db.query_tickets(db, id=id)
    return f'{result.body}'

def cron_receieve():
    """Recieve mail with IMAPClient and process mail for new tickets/comments"""
    if config.get('mail_server', None) is None:
        abort(400)
    mail = Mail.Mail(config)
    mail.get_mail()
    results = mail.process_mail(db)
    return f'{results}'

def cron_review():
    #query logs for unflagged
    if config.get('mail_server', None) is None:
        abort(400)
    logs = Db.query_logs(db, trigger=False)
    result = logs
    #check event against config for notification
    notification = config.get("notification", [None])
    for log in logs:
        if log.event in notification:
            if log.table in notification:
                if log.table == 'comments':
                    ticket_id = Db.query_comments(db, comment_id=log.item_id).ticket
                else:
                    ticket_id = log.item_id
                ticket = Db.query_tickets(db, id=ticket_id)
                table = log.table.capitalize()
                subject = f"#Ticket {ticket_id} {log.event}ed {table}"
                if log.source:
                    subject = subject + f" by {log.source}"
                recipients = ticket.assigned[0].email
                if ticket.cc is not None:
                    recipients = recipients + "," + ticket.cc
                submit = json.dumps(dict(
                    ticket_id = log.item_id,
                    subject = subject,
                    recipients =  recipients))
                send = str(request.base_url).replace('test','send')
                Db.activity_trigger(db, id=log.item_id, trigger=True)
                result = requests.post(send, json=submit)
    return f'{result}'

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

sched = BackgroundScheduler(daemon=True)
#sched.add_job(cron_review,'interval',minutes=5)
#sched.add_job(cron_receieve,'interval',minutes=5)
sched.start()

# export environment='dev' for no ssl or debugging
if __name__ == "__main__":
    if(os.environ['environment'] == 'dev'):
        print('Running in Dev')
        app.run(host="0.0.0.0", debug=True)
    else:
        print('Running in Prod')
        app.run(host="0.0.0.0", ssl_context=('../server.x509', '../server.key'))