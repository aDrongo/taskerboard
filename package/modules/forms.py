from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField, BooleanField, SelectMultipleField
from wtforms.fields.html5 import EmailField
from flask_login import UserMixin
import modules.database as Db
import hashlib

class LoginUser(UserMixin):
    """User for Flask Session"""
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

class LoginForm(Form):
    username = TextField('username:', [validators.required(), validators.length(max=64)])
    #email = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password', validators=[validators.DataRequired(message="Password field is required")])
    remember_me = BooleanField('remember_me')
    submitLogin = SubmitField('submit', [validators.DataRequired()])

class CommentForm(Form):
    """WTForm for Comments"""
    comment = TextAreaField('Comment:')
    submitComment = SubmitField('submit')

class TicketInsertForm(Form):
    """WTForm for Inserting a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    tags = TextField('tags')
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    created_by = TextField('Created By:')
    assigned = SelectField('Assigned:')
    submitInsertTicket = SubmitField('submit')

class TicketUpdateForm(Form):
    """WTForm for Updating a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    tags = TextField('tags')
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    created_by = TextField('Created By:')
    assigned = SelectField('Assigned:')
    submitUpdateTicket = SubmitField('submit')

class TicketSearchForm(Form):
    """WTForm for Searching Tickets"""
    search = TextField('Search:', [validators.required(), validators.length(max=140)])
    submitSearch = SubmitField('search')

class UserInsertForm(Form):
    """WTForm for Inserting a User"""
    username = TextField('Username:', [validators.required(), validators.length(max=140)])
    email = EmailField('Email:')
    password = PasswordField('Password:', [validators.required(), validators.length(max=140)])
    submitInsertUser = SubmitField('submit')

class UserUpdateForm(Form):
    """WTForm for Updating a User"""
    username = SelectField('Username:')
    email = EmailField('Email:')
    password = PasswordField('Password:')
    submitUpdateUser = SubmitField('submit')

def ticket_insert_form(Form, Db, user=None):
    """Insert a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = Db.Priority[f'{Form.priority.data}'].value
    tags = Form.tags.data
    status = Db.Status[f'{Form.status.data}'].value
    created_by = user
    if Form.assigned.data and Form.assigned.data != 'None':
        assigned = Form.assigned.data
    else:
        assigned = None
    due_by = None
    Db.insert_ticket(subject=subject,body=body,priority=priority, created_by=created_by, status=status, tags=tags, assigned=assigned, due_by=due_by)
    result = Db.query_tickets(subject=subject)[0]
    return result

def ticket_update_form(Form, Db, id):
    """"Update a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = Db.Priority[f'{Form.priority.data}'].value
    tags = Form.tags.data
    status = Db.Status[f'{Form.status.data}'].value
    if Form.assigned.data and Form.assigned.data != 'None':
        assigned = Form.assigned.data
    else:
        assigned = None
    due_by = None
    created_by = Form.created_by.data
    result = Db.update_ticket(id=id, subject=subject, body=body, status=status, priority=priority, created_by=created_by, assigned=assigned, tags=tags, due_by=due_by)
    return result

def user_insert_form(Form, Db):
    username = Form.username.data
    email = Form.email.data
    password = Form.password.data
    result = Db.insert_user(username=username, email=email, password=password)
    return result

def user_update_form(Form, Db):
    username = Form.username.data
    email = Form.email.data
    password = Form.password.data
    result = Db.update_user(username=username, email=email, password=password)
    return result