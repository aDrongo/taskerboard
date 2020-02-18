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
    id = None

    def insert_comment(self, db, id):
        comment = self.comment.data
        result = Db.insert_comment(db, ticket=id, created_by=self.id, body=comment)
        return result

class TicketInsertForm(Form):
    """WTForm for Inserting a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    tags = TextField('tags')
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    created_by = TextField('Created By:')
    cc = TextField('CC')
    assigned = SelectField('Assigned:')
    submitInsertTicket = SubmitField('submit')
    id = None

    def ticket_insert(self, db):
        """Insert a Ticket from Form results"""
        subject = self.subject.data
        body = self.body.data
        priority = Models.Priority[f'{self.priority.data}'].value
        tags = self.tags.data
        status = Models.Status[f'{self.status.data}'].value
        created_by = self.created_by.data
        cc = self.cc.data
        if self.assigned.data and self.assigned.data != 'None':
            assigned = self.assigned.data
        else:
            assigned = None
        due_by = None
        Db.insert_ticket(db, subject=subject,body=body,priority=priority, created_by=created_by, status=status, tags=tags, assigned=assigned, due_by=due_by, cc=cc, user_id=self.id)
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
    cc = TextField('CC')
    assigned = SelectField('Assigned:')
    submitUpdateTicket = SubmitField('submit')
    id = None

    def ticket_update(self, db, id):
        """"Update a Ticket from Form results, 
        for activity tracking to not get flooded we must only submit values that are different, 
        to do this we compare against the original ticket values"""
        original = Db.query_tickets(db, id=id)
        print(original.tags[0].body)
        original.tag = [str(tag) for tag in original.tags]
        if self.subject.data != original.subject:
            subject = self.subject.data
        else:
            subject = None
        if self.body.data != original.body:
            body = self.body.data
        else:
            body = None
        if self.priority.data != original.priority.name: 
            priority = Models.Priority[f'{self.priority.data}'].value
        else:
            priority = None
        if self.tags.data != (",".join(original.tag)):
            tags = self.tags.data
        else:
            tags = None
        if self.status.data != original.status.name:
            status = Models.Status[f'{self.status.data}'].value
        else:
            status = None
        if self.cc.data != str(original.cc):
            cc = self.cc.data
        else:
            cc = None
        if self.assigned.data and self.assigned.data != 'None' and self.assigned.data != f'{original.assigned[0]}':
            assigned = self.assigned.data
        else:
            assigned = None
        due_by = None
        print(original.created_by)
        if self.created_by.data != original.created_by:
            created_by = self.created_by.data
        else:
            created_by = None
        result = Db.update_ticket(db, id=id, subject=subject, body=body, status=status, priority=priority, created_by=created_by, assigned=assigned, tags=tags, due_by=due_by, cc=cc, user_id=self.id)
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
    id = None

    def user_insert(self, db):
        username = self.username.data
        email = self.email.data
        password = self.password.data
        result = Db.insert_user(db, username=username, email=email, password=password, user=self.id)
        return result

class UserUpdateForm(Form):
    """WTForm for Updating a User"""
    username = SelectField('Username:')
    email = EmailField('Email:')
    password = PasswordField('Password:')
    submitUpdateUser = SubmitField('submit')
    id = None

    def user_update(self, db):
        username = self.username.data
        email = self.email.data
        password = self.password.data
        result = Db.update_user(db, username=username, email=email, password=password, user=self.id)
        return result

class ImportDataForm(FlaskForm):
    """WTform for Importing data"""
    file = FileField()
    id = None

    def submit(self, db, id=None):
        filepath = os.getcwd() + "/upload.tmp"
        self.file.data.save(filepath)
        with open(filepath) as file:
            data = json.load(file)
        os.remove(filepath)
        result = Db.bulk_insert_ticket(db, data, user=id)
        return result

class LogSearchForm(FlaskForm):
    """WTForm for searching logs"""
    timestamp = TextField('timestamp')
    item_id = TextField('item_id')
    event = SelectField('event', choices=[("Any","Any"),("Insert","Insert"),("Update","Update"),("Delete","Delete")])
    table = SelectField('table', choices=[("Any","Any"),("tickets","tickets"),("users","users"),("comments","comments")])
    details = TextField('details')
    source = TextField("source")
    trigger = SelectField('trigger', choices=[("Any","Any"),("True","True"),("False","False")])
    submitSearch = SubmitField('search')

    def log_search_query(self):
        query = ""
        if self.timestamp.data:
            query = query + "&timestamp=" + str(self.timestamp.data)
        if self.item_id.data:
            query = query + "&item_id=" + str(self.item_id.data)
        if self.event.data and self.event.data != "Any":
            query = query + "&event=" + str(self.event.data)
        if self.table.data and self.table.data != "Any":
            query = query + "&table=" + str(self.table.data)
        if self.details.data:
            query = query + "&details=" + str(self.details.data)
        if self.source.data:
            query = query + "&source=" + str(self.source.data)
        if self.trigger.data and self.trigger.data != "Any":
            query = query + "&trigger=" + str(self.trigger.data)
        return query

class TicketForms():
    """Class to hold Ticket Forms"""
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
                self.commentForm.id = user_id
                self.ticketInsertForm.id = user_id
                self.ticketUpdateForm.id = user_id

class UserForms():
    """Class to hold User Forms"""

    def __init__(self, db, user_id=None):
        users = [(user.username, user.username) for user in Db.query_users(db)]
        self.userInsertForm = UserInsertForm(request.form)
        self.userUpdateForm = UserUpdateForm(request.form)
        self.userUpdateForm.username.choices = users
        self.userInsertForm.id = user_id
        self.userUpdateForm.id = user_id


class SettingsForms():
    """Class to hold Settings Forms"""

    def __init__(self):
        self.importDataForm = ImportDataForm()