import sqlalchemy as db
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum

# For class to create table
Base = declarative_base()


class Priority(enum.Enum):
    High = 1
    Medium = 2
    Low = 3

class Status(enum.Enum):
    Open = 1
    Closed = 2

class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Tickets(Base):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status))
    priority = db.Column(db.Enum(Priority))
    subject = db.Column(db.String(140))
    body = db.Column(db.String(1280))
    created_at = db.Column(db.String(19), index=True, default=str(datetime.utcnow())[:19])
    updated_at = db.Column(db.String(19), index=True, default=str(datetime.utcnow())[:19])
    created_by = db.Column(db.String(140))
    assigned = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'{self.body}'

class Comments(Base):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    created_at = db.Column(db.String(19), index=True, default=str(datetime.utcnow())[:19])
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(1280))
    

class Database():
    def __init__(self, database):
        self.engine = db.create_engine(f'sqlite:///{database}', connect_args={'check_same_thread': False})
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.metadata = db.MetaData()
        Base.metadata.create_all(self.engine)


db = Database('app.db')


#Insert user
def insert_user(username, email):
    insert = User(username=f'{username}', email=f'{email}')
    db.session.add(insert)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


#Update User
def update_user(username, new_username, new_email):
    update = db.session.query(User).filter(User.username == f'{username}').update({'username': f'{new_username}','email':f'{new_email}'})
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

#Delete User
def delete_user(username):
    delete = db.session.query(User).filter(User.username == f'{username}').delete()
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

#Insert Ticket
def insert_ticket(subject,body,priority,created_by):
    insert = Tickets(status=Status(1), subject=f'{subject}', body=f'{body}', priority= Priority(priority), created_by=f'{created_by}')
    db.session.add(insert)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

#Update ticket
def update_ticket(id, status, subject, body, priority, created_by, assigned):
    time = str(datetime.utcnow())[:19]
    update = db.session.query(Tickets).filter(Tickets.id == id).update({
        'status': Status(status),
        'subject':f'{subject}',
        'body': f'{body}',
        'priority': Priority(priority),
        'created_by': f'{created_by}',
        'updated_at': time,
        'assigned': f'{assigned}'})
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

#Insert Comment
def insert_comment(ticket, created_by, body):
    insert = Comments(ticket=f'{ticket}', body=f'{body}',created_by=f'{created_by}')
    db.session.add(insert)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

#Query User
def query_user_id(username):
    result = db.session.query(User).filter(User.username == username).first()
    return result.id

#Query Users Tickets
def query_user_tickets(id):
    result = db.session.query(Tickets).filter(User.id == id).all()
    return result

#Query Ticket
def query_ticket(id):
    result = db.session.query(Tickets).filter(Tickets.id == id).first()
    return result

#Query Tickets
def query_tickets_all():
    result = db.session.query(Tickets).all()
    return result

#Query Tickets Open
def query_tickets_open():
    result = db.session.query(Tickets).filter(Tickets.status == True).all()
    return result

#Query Tickets Closed
def query_tickets_closed():
    result = db.session.query(Tickets).filter(Tickets.status == False).all()
    return result

#Query comments
def query_comments(ticket):
    result = db.session.query(Comments).filter(Comments.ticket == ticket).all()
    return result