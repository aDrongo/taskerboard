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