from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField, BooleanField, SelectMultipleField, FileField
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_login import UserMixin
from flask import request
import hashlib

import modules.database as Db
import modules.models as Models


class LoginUser(UserMixin):
    """User for Flask Session"""
    #is_authenticated(boolean)
    #is_active(boolean)
    #is_anonymous(boolean)
    #get_id(unicode)

    def __init__(self, db, username):
        """Retrieve user from Db"""
        self.auth = None
        user = Db.query_users(db, username)[0]
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

    def insert_comment(self, db, id, user_id):
        comment = self.comment.data
        result = Db.insert_comment(db, ticket=id, created_by=user_id, body=comment)
        return result

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

    def ticket_insert(self, db, user=None):
        """Insert a Ticket from Form results"""
        subject = self.subject.data
        body = self.body.data
        priority = Models.Priority[f'{self.priority.data}'].value
        tags = self.tags.data
        status = Models.Status[f'{self.status.data}'].value
        created_by = user
        if self.assigned.data and self.assigned.data != 'None':
            assigned = self.assigned.data
        else:
            assigned = None
        due_by = None
        Db.insert_ticket(db, subject=subject,body=body,priority=priority, created_by=created_by, status=status, tags=tags, assigned=assigned, due_by=due_by)
        result = Db.query_tickets(db, subject=subject)[0]
        return result

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

    def ticket_update(self, db, id):
        """"Update a Ticket from Form results"""
        subject = self.subject.data
        body = self.body.data
        priority = Models.Priority[f'{self.priority.data}'].value
        tags = self.tags.data
        status = Models.Status[f'{self.status.data}'].value
        if self.assigned.data and self.assigned.data != 'None':
            assigned = self.assigned.data
        else:
            assigned = None
        due_by = None
        created_by = self.created_by.data
        result = Db.update_ticket(db, id=id, subject=subject, body=body, status=status, priority=priority, created_by=created_by, assigned=assigned, tags=tags, due_by=due_by)
        return result

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

    def user_insert_form(self, db):
        username = self.username.data
        email = self.email.data
        password = self.password.data
        result = Db.insert_user(db, username=username, email=email, password=password)
        return result

class UserUpdateForm(Form):
    """WTForm for Updating a User"""
    username = SelectField('Username:')
    email = EmailField('Email:')
    password = PasswordField('Password:')
    submitUpdateUser = SubmitField('submit')

    def user_update_form(self, db):
        username = self.username.data
        email = self.email.data
        password = self.password.data
        result = Db.update_user(db, username=username, email=email, password=password)
        return result

class ImportDataForm(FlaskForm):
    """WTform for Importing data"""
    file = FileField()

class Forms():
    """Class to hold Forms"""
    ticketUpdateForm = None
    commentForm = None

    def __init__(self, db, ticket=None, user_id=None):
        users = [(user.username, user.username) for user in Db.query_users(db)]
        self.searchForm = TicketSearchForm(request.form)
        self.ticketInsertForm = TicketInsertForm(request.form)
        self.ticketInsertForm.assigned.choices = users
        self.ticketInsertForm.assigned.choices.append(('None', 'None'))

        if ticket:
            self.ticketUpdateForm = TicketUpdateForm(request.form)
            self.ticketUpdateForm.assigned.choices = users

            if user_id:
                self.commentForm = CommentForm(request.form)