import sqlalchemy as Db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

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
assigned_table = Db.Table('assigned', Base.metadata,
    Db.Column('users_username', Db.String(140), Db.ForeignKey('users.username')),
    Db.Column('assigned_tickets_id', Db.String(140), Db.ForeignKey('tickets.id'))
)

#Many to many table for Tags to Tickets
tag_groups_table = Db.Table('tag_groups', Base.metadata,
    Db.Column('tag_tickets_id', Db.String(140), Db.ForeignKey('tickets.id')),
    Db.Column('tags_id', Db.String(140), Db.ForeignKey('tags.id'))
)

class User(Base):
    """Class for Users table"""
    __tablename__ = 'users'
    username = Db.Column(Db.String(64), primary_key=True)
    email = Db.Column(Db.String(120), unique=True)
    password_hash = Db.Column(Db.String(128))

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
    id = Db.Column(Db.Integer, primary_key=True)
    body = Db.Column(Db.String(140))

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
    id = Db.Column(Db.Integer, primary_key=True)
    status = Db.Column(Db.Enum(Status))
    priority = Db.Column(Db.Enum(Priority))
    subject = Db.Column(Db.String(140))
    body = Db.Column(Db.String(1280))
    created_at = Db.Column(Db.String(19), default=str(datetime.utcnow())[:19])
    updated_at = Db.Column(Db.String(19), default=str(datetime.utcnow())[:19])
    due_by = Db.Column(Db.String(19))
    created_by = Db.Column(Db.String(140))
    cc = Db.Column(Db.String(1280))
    assigned = relationship("User", secondary=assigned_table)
    tags = relationship("Tags", secondary=tag_groups_table)

    def repr(self):
        return str(dict(
            id=self.id,
            subject = self.subject
        ))

    def to_dict(self):
        return dict(
        id=self.id,
        status= self.status.name,
        priority = self.priority.name,
        subject = self.subject,
        body = self.body,
        created_at = self.created_at,
        updated_at = self.updated_at,
        due_by = self.due_by,
        created_by = self.created_by,
        cc = self.cc,
        assigned = [item.to_dict_user() for item in self.assigned],
        tags = [item.to_dict() for item in self.tags])

class Comments(Base):
    """Class for Comments table"""
    __tablename__ = 'comments'
    id = Db.Column(Db.Integer, primary_key=True)
    ticket = Db.Column(Db.Integer, Db.ForeignKey('tickets.id'))
    created_at = Db.Column(Db.String(19), index=True, default=str(datetime.utcnow())[:19])
    created_by = Db.Column(Db.Integer, Db.ForeignKey('users.username'))
    body = Db.Column(Db.String(1280))

    def __repr__(self):
        return str(dict(
            id = self.id,
            ticket = self.ticket,
            body = self.body,
            created_by = self.created_by
        ))

    def to_dict(self):
        return dict(
            id = self.id,
            ticket = self.ticket,
            created_at = self.created_at,
            created_by = self.created_by,
            body = self.body)

class Events(Base):
    """Acivitiy Log"""
    __tablename__ = 'events'
    id = Db.Column(Db.Integer, primary_key=True)
    timestamp = Db.Column(Db.String(19), default=str(datetime.utcnow())[:19])
    event = Db.Column(Db.String(140))
    table = Db.Column(Db.String(140))
    item_id = Db.Column(Db.String(140))
    details = Db.Column(Db.String(1280))
    source = Db.Column(Db.String(140))
    trigger = Db.Column(Db.Boolean, default=False)

    def __repr__(self):
        return str(dict(
            id = self.id,
            timestamp = self.timestamp,
            event = self.event,
            table = self.table,
            item_id = self.item_id
        ))

    def to_dict(self):
        return dict(
            id = self.id,
            timestamp = self.timestamp,
            event = self.event,
            table = self.table,
            item_id = self.item_id,
            details = sefl.details,
            source = self.source,
            trigger = self.trigger)