from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
import modules.database as Db

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
    submitInsertTicket = SubmitField('submit')

class TicketUpdateForm(Form):
    """WTForm for Updating a Ticket"""
    subject = TextField('Subject:', [validators.required(), validators.length(max=140)])
    body = TextAreaField('Body:', [validators.required(), validators.length(max=1280)])
    priority = SelectField('Priority', choices=[('High','High'),('Medium','Medium'),('Low','Low')])
    tags = TextField('tags')
    status = SelectField('Status', choices=[('Open','Open'),('Working','Working'),('Waiting','Waiting'),('Closed','Closed')])
    created_by = TextField('Created By:', [validators.required(), validators.length(max=140)])
    submitUpdateTicket = SubmitField('submit')

def ticket_insert_form(Form, Db, user=None):
    """Insert a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = Db.Priority[f'{Form.priority.data}'].value
    tags = Form.tags.data
    status = Db.Status[f'{Form.status.data}'].value
    created_by = user
    Db.insert_ticket(subject,body,priority, created_by, status, tags)
    result = Db.query_ticket_subject(subject)
    return result

def ticket_update_form(Form, Db, id):
    """"Update a Ticket from Form results"""
    subject = Form.subject.data
    body = Form.body.data
    priority = Db.Priority[f'{Form.priority.data}'].value
    tags = Form.tags.data
    status = Db.Status[f'{Form.status.data}'].value
    assigned = None
    due_by = None
    created_by = Form.created_by.data
    result = Db.update_ticket(id, subject, body, status, priority, created_by, assigned, tags, due_by)
    return result