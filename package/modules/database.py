import sqlalchemy as db
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
import enum
import hashlib

# For class to create table
Base = declarative_base()

class Priority(enum.Enum):
    """Priority Levels"""
    High = 1
    Medium = 2
    Low = 3

class Status(enum.Enum):
    """Status Levels"""
    Open = 1
    Working = 2
    Waiting = 3
    Closed = 4

#Many to many table for Users to Tickets
assigned_table = db.Table('assigned', Base.metadata,
    db.Column('users_username', db.String(140), db.ForeignKey('users.username')),
    db.Column('assigned_tickets_id', db.String(140), db.ForeignKey('tickets.id'))
)

#Many to many table for Tags to Tickets
tag_groups_table = db.Table('tag_groups', Base.metadata,
    db.Column('tag_tickets_id', db.String(140), db.ForeignKey('tickets.id')),
    db.Column('tags_id', db.String(140), db.ForeignKey('tags.id'))
)

class User(Base):
    """Class for Users table"""
    __tablename__ = 'users'
    username = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'{self.username}'
    
    def to_dict(self):
        return dict(
            username=self.username,
            email = self.email,
            password_hash = self.password_hash)
    
    def to_dict_user(self):
        return dict(
            username=self.username,
            email = self.email)

class Tags(Base):
    """Class for Tags table"""
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))

    def __repr__(self):
        return f'{self.body}'

    def to_dict(self):
        return dict(
        id=self.id,
        body = self.body)
    
    def to_string(self):
        return f'{self.body}'


class Tickets(Base):
    """Class for Tickets table"""
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status))
    priority = db.Column(db.Enum(Priority))
    subject = db.Column(db.String(140))
    body = db.Column(db.String(1280))
    created_at = db.Column(db.String(19), default=str(datetime.utcnow())[:19])
    updated_at = db.Column(db.String(19), default=str(datetime.utcnow())[:19])
    due_by = db.Column(db.String(19))
    created_by = db.Column(db.String(140))
    assigned = relationship("User", secondary=assigned_table)
    tags = relationship("Tags", secondary=tag_groups_table)

    def __repr__(self):
        return f'{self.subject}'

    def to_dict(self):
        return dict(
        id=self.id,
        status= self.status.name,
        priority = self.priority.name,
        subject = self.subject,
        body = self.body,
        created_at = self.created_at,
        due_by = self.due_by,
        created_by = self.created_by,
        assigned = [item.to_dict_user() for item in self.assigned],
        tags = [item.to_dict() for item in self.tags])

class Comments(Base):
    """Class for Comments table"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    created_at = db.Column(db.String(19), index=True, default=str(datetime.utcnow())[:19])
    created_by = db.Column(db.Integer, db.ForeignKey('users.username'))
    body = db.Column(db.String(1280))

    def __repr__(self):
        return f'{self.body}'

    def to_dict(self):
        return dict(
            id = self.id,
            ticket = self.ticket,
            created_at = self.created_at,
            created_by = self.created_by,
            body = self.body)

class Database():
    """Class to connect to Database"""
    def __init__(self, database):
        self.engine = db.create_engine(f'sqlite:///{database}', connect_args={'check_same_thread': False})
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.metadata = db.MetaData()
        Base.metadata.create_all(self.engine)

# Connect to DB
db = Database('app.db')

def insert_user(username, email, password):
    """Insert user"""
    hash = hashlib.md5()
    password = password.encode()
    hash.update(password)
    hash = hash.hexdigest()
    insert = User(username=f'{username}', email=f'{email}', password_hash=f'{hash}')
    db.session.add(insert)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def update_user(username, email, password):
    """Update User"""
    query = db.session.query(User).filter(User.username == f'{username}')
    update_dict = {}
    if email:
        update_dict['email'] = email
    if password:
        hash = hashlib.md5()
        password = password.encode()
        hash.update(password)
        hash = hash.hexdigest()
        update_dict['password_hash'] = hash
    update = db.session.query(User).filter(User.username == f'{username}').update(update_dict)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def delete_user(username):
    """Delete User"""
    delete = db.session.query(User).filter(User.username == f'{username}').delete()
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def get_user(username):
    result = db.session.query(User).filter(User.username == f'{username}').first()
    return result

def get_users():
    result = db.session.query(User).all()
    return result

def check_password(username, password):
    hash = hashlib.md5()
    password = password.encode()
    hash.update(password)
    hash = hash.hexdigest()
    password_hash = db.session.query(User).filter(User.username == f'{username}').first().password_hash
    return (password_hash == hash)


def insert_ticket(subject,body=None,priority=None, created_by=None, status=None, tags=None, assigned=None, due_by=None):
    """Insert Ticket"""

    print('test')
    time = str(datetime.utcnow())[:19]
    insert = Tickets(
        subject= f'{subject}',
        updated_at= time)
    if body:
        insert.body = f'{body}'
    if status:
        if (isinstance(status, int)):
            status = Status(status)
        else:
            status = Status[status]
        insert.status = status
    else:
        insert.status = Status(1)
    if priority:
        if (isinstance(priority, int)):
            priority = Priority(priority)
        else:
            priority = Priority[priority]
        insert.priority = Priority(priority)
    else:
        insert.priority = Priority(2)
    if tags:
        tag_obj = db.session.query(Tags).filter(Tags.body.in_(tags)).all()
        if tag_obj is None:
            tags = tags.split(',')
            for tag in tags:
                tag_tmp = Tag()
                tag_tmp.body = tag
                db.session.add(tag_tmp)
            tag_obj = db.session.query(Tags).filter(Tags.body.in_(tags)).all()
        insert.tags = [tag for tag in tag_obj]
    if created_by:
        insert.created_by = f'{created_by}'
    if assigned:
        users = db.session.query(User).filter(User.username.in_(assigned)).all()
        insert.assigned = [user for user in users]
    if due_by:
        insert.due_by = f'{due_by}'
    db.session.add(insert)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def update_ticket(id, subject=None, body=None, status=None, priority=None, created_by=None, assigned=None, tags=None, due_by=None):
    """Update ticket"""
    time = str(datetime.utcnow())[:19]
    update_dict = {
        'id': id,
        'updated_at': time}
    if subject:
        update_dict['subject'] = f'{subject}'
    if body:
        update_dict['body'] = f'{body}'
    if status:
        #allow converting either integer or string to enumerator
        if (isinstance(status, int)):
            status = Status(status)
        else:
            status = Status[status]
        update_dict['status'] = status
    if priority:
        #allow converting either integer or string to enumerator
        if (isinstance(priority, int)):
            priority = Priority(priority)
        else:
            priority = Priority[priority]
        update_dict['priority'] = Priority(priority)
    if created_by:
        update_dict['created_by'] = f'{created_by}'
    if due_by:
        update_dict['due_by'] = f'{due_by}'
    print('-----')
    update = db.session.query(Tickets).filter(Tickets.id == id).update(update_dict)
    if tags or assigned:
        ticket = db.session.query(Tickets).filter(Tickets.id == id).first()
    # Add Tags, needs a seperate call because of it's relationship
    if tags:
        # retrieve tags object to add, if not found then create them and retireve object.
        tag_obj = db.session.query(Tags).filter(Tags.body.ilike(tags)).all()
        if tag_obj is None:
            tags = tags.split(',') # allows receiving multiple tags
            for tag in tags:
                tag_tmp = Tag()
                tag_tmp.body = tag
                db.session.add(tag_tmp)
            tag_obj = db.session.query(Tags).filter(Tags.body.ilike(tags)).all()
        ticket.tags = [tag for tag in tag_obj]
    # Add assigned, needs a seperate call because of it's relationship
    if assigned:
        users = db.session.query(User).filter(User.username.ilike(assigned)).all()
        ticket.assigned = [user for user in users]
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def insert_comment(ticket, created_by, body):
    """Insert Comment"""
    time = str(datetime.utcnow())[:19]
    insert = Comments(ticket=ticket, body=f'{body}',created_by=f'{created_by}')
    #update = db.session.query(Tickets).filter(Tickets.id == ticket).update({'updated_at':time})
    db.session.add(insert)
    #db.session.add(update)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def query_tickets(id=None, subject=None, status=None,tags=None,assigned=None,order=None):
    """Query all tickets with defined filters"""
    # Base Query
    query = db.session.query(Tickets)
    if id:
        return query.filter(Tickets.id == id).first()
    # get Order
    if order == 'updated_at':
        order = Tickets.updated_at.desc()
    elif order == 'created_at':
        order = Tickets.created_at.desc()
    elif order == 'id':
        order = Tickets.id.desc()
    elif order == 'assigned':
        order = Tickets.assigned.desc()
    elif order == 'priority':
        order = Tickets.priority.asc()
    else:
        order = Tickets.id.desc()
    # Add Subject filter
    if subject:
        subject = Tickets.subject.ilike(subject)
        query = query.filter(subject)
    # Add Status filter
    if status:
        status = status.capitalize()
        try:
            status = Status[status]
            query = query.filter(Tickets.status == status)
        except:
            pass
    # Add Assigned filter
    if assigned:
        user = db.session.query(User).filter(User.username.contains(assigned)).first()
        if user:
            assigned = Tickets.assigned.contains(user)
            query = query.filter(assigned)
    # Add Tags filter
    if tags:
        tag = db.session.query(Tags).filter(Tags.body.contains(tags)).first()
        if tag:
            tags = Tickets.tags.contains(tag)
            query = query.filter(tags)
    # Run Query
    result = query.order_by(order).all()
    return result

def query_comments(ticket,order=None):
    """Query all comments for a ticket"""
    if order == 'created_at':
        order = Comments.created_at.desc()
    else:
        order = Comments.id.desc()
    result = db.session.query(Comments).filter(Comments.ticket == ticket).order_by(order).all()
    return result

def convert_to_dict(items):
    result = []
    try:
        for item in items:
            result.append(item.to_dict())
    except:
        result.append(items.to_dict())
    return result
