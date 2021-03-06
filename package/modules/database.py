import hashlib
import sqlalchemy as Db
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import modules.models as Models

class Database():
    """Class to connect to Database"""
    def __init__(self, database):
        self.engine = Db.create_engine(f'sqlite:///{database}', connect_args={'check_same_thread': False})
        self.connection = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.metadata = Db.MetaData()
        Models.Base.metadata.create_all(self.engine)

def log_activity(db, event=None, table=None, item_id=None, details=None, source=None, trigger=None):
    time = str(datetime.utcnow())[:19]
    insert = Models.Logs(timestamp=time)
    if event:
        insert.event = event
    if table:
        insert.table = table
    if item_id:
        insert.item_id = item_id
    if details:
        insert.details = details
    if source:
        insert.source = source
    if trigger:
        insert.trigger = trigger
    db.session.add(insert)
    pass

def activity_trigger(db, id, trigger):
    if (trigger is not True) and (trigger is not False):
        return False
    else:
        db.session.query(Models.Logs).filter(Models.Logs.id == id).update({"trigger": trigger})
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

def insert_user(db, username, email, password, user=None):
    """Insert user"""
    hash = hashlib.md5()
    password = password.encode()
    hash.update(password)
    hash = hash.hexdigest()
    insert = Models.User(username=f'{username}', email=f'{email}', password_hash=f'{hash}')
    db.session.add(insert)
    db.session.flush()
    details = str(insert.to_dict_user())
    try:
        log_activity(db, event="Insert", table="users", item_id=insert.username, details=details, source=user)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def update_user(db, username, email, password, user=None):
    """Update User"""
    query = db.session.query(Models.User).filter(Models.User.username == f'{username}')
    update_dict = {}
    if email:
        update_dict['email'] = email
    if password:
        hash = hashlib.md5()
        password = password.encode()
        hash.update(password)
        hash = hash.hexdigest()
        update_dict['password_hash'] = hash
    update = db.session.query(Models.User).filter(Models.User.username == f'{username}').update(update_dict)
    db.session.flush()
    try:
        log_activity(db, event="Update", table="users", item_id=username, details=str(update_dict), source=user)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def delete_user(db, username, user=None):
    """Delete User"""
    delete = db.session.query(Models.User).filter(Models.User.username == f'{username}').delete()
    db.session.flush()
    try:
        log_activity(db, event="Delete", table="users", item_id=username, source=user)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def check_password(db, username, password):
    hash = hashlib.md5()
    password = password.encode()
    hash.update(password)
    hash = hash.hexdigest()
    password_hash = db.session.query(Models.User).filter(Models.User.username == f'{username}').first().password_hash
    return (password_hash == hash)

def insert_tags(db, tags):
    tags = tags.split(',')
    for tag in tags:
        tag = tag.strip()
        tag_tmp = Models.Tags(body=tag)
        db.session.add(tag_tmp)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def insert_ticket(db, subject,body=None, status=None, priority=None, created_by=None, tags=None, assigned=None, due_by=None, cc=None, user_id=None):
    """Insert Ticket"""
    time = str(datetime.utcnow())[:19]
    insert = Models.Tickets(
        subject= f'{subject}',
        updated_at= time)
    if body:
        insert.body = f'{body}'
    if status:
        if (isinstance(status, int)):
            status = Models.Status(status)
        else:
            status = Models.Status[status]
        insert.status = status
    else:
        insert.status = Models.Status(1)
    if priority:
        if (isinstance(priority, int)):
            priority = Models.Priority(priority)
        else:
            priority = Models.Priority[priority]
        insert.priority = Models.Priority(priority)
    else:
        insert.priority = Models.Priority(2)
    if tags:
        tags = tags.split(',')
        for tag in tags:
            tag_obj = query_tags(db, tag)
            if tag_obj is None:
                insert_tags(db, tag)
        tag_list = query_tags(db, tags)
        insert.tags = [tag for tag in tag_list]
    if created_by:
        insert.created_by = f'{created_by}'
    if assigned:
        users = query_users(db, assigned)
        insert.assigned = [user for user in users]
    if due_by:
        insert.due_by = f'{due_by}'
    if cc:
        insert.cc = f'{cc}'
    db.session.add(insert)
    db.session.flush()
    details = str(insert.to_dict())
    try:
        log_activity(db, event="Insert", table="tickets", item_id=insert.id, details=details, source=user_id)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def bulk_insert_ticket(db, data, user_id=None):
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
        insert_ticket(db,
            subject=ticket['subject'],
            body=ticket.get('body', None),
            status=ticket.get('status', None),
            priority=ticket.get('priority', None),
            tags=tags,
            created_by=ticket.get('created_by', None),
            assigned=assigned,
            due_by=ticket.get('due_by', None),
            user_id=user_id)

def update_ticket(db, id, subject=None, body=None, status=None, priority=None, created_by=None, assigned=None, tags=None, due_by=None, cc=None, user_id=None):
    """Update ticket"""
    time = str(datetime.utcnow())[:19]
    activity = []
    update_dict = {
        'id': id,
        'updated_at': time}
    if subject:
        update_dict['subject'] = f'{subject}'
        activity.append("Subject")
    if body:
        update_dict['body'] = f'{body}'
        activity.append("Body")
    if status:
        #allow converting either integer or string to enumerator
        if (isinstance(status, int)):
            status = Models.Status(status)
        else:
            status = Models.Status[status]
        update_dict['status'] = status
        activity.append(f"Status to {status.name}")
    if priority:
        #allow converting either integer or string to enumerator
        if (isinstance(priority, int)):
            priority = Models.Priority(priority)
        else:
            priority = Models.Priority[priority]
        update_dict['priority'] = Models.Priority(priority)
        activity.append(f"Priority to {priority.name}")
    if created_by:
        update_dict['created_by'] = f'{created_by}'
        activity.append(f"Created By to {created_by}")
    if due_by:
        update_dict['due_by'] = f'{due_by}'
        activity.append(f"Due By to {due_by}")
    if cc:
        update_dict['cc'] = f'{cc}'
        activity.append(f"CC to {cc}")
    # Update ticket
    update = db.session.query(Models.Tickets).filter(Models.Tickets.id == id).update(update_dict)
    # Joined Tables need seperate call to update
    ticket = db.session.query(Models.Tickets).filter(Models.Tickets.id == id).first()
    # Add Tags, needs a seperate call because of it's relationship
    if tags:
        # retrieve tags object to add, if not found then create them and retireve object.
        tags_split = tags.split(',')
        for tag in tags_split:
            tag_obj = query_tags(db, tag)
            if tag_obj is None:
                insert_tags(db, tag)
        tag_list = query_tags(db, tags_split)
        ticket.tags = [tag for tag in tag_list]
        update_dict['tags'] = ticket.tags
        activity.append(f"Tags to {tags}")
    # Add assigned, needs a seperate call because of it's relationship
    if assigned:
        users = db.session.query(Models.User).filter(Models.User.username.is_(assigned)).all()
        ticket.assigned = [user for user in users]
        update_dict['assigned'] = ticket.assigned
        activity.append(f"Assigned to {assigned}")
    activity = ",".join(activity)
    #Write activity to comment
    insert_comment(db, ticket=id, created_by=user_id, body=activity, variety=Models.CommentVariety(3))
    try:
        log_activity(db, event="Update", table="tickets", item_id=id, details=str(update_dict), source=user_id)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def insert_comment(db, ticket, created_by, body, variety=None):
    """Insert Comment"""
    print('1')
    time = str(datetime.utcnow())[:19]
    #Check if variety is enum, if it's not the enum then convert it.
    if (variety == None):
        variety = Models.CommentVariety(1)
    else:
        if isinstance(variety, Models.CommentVariety) == False:
            variety = str(variety).lower()
            print(variety)
            if (variety == "external") or (variety == '1'):
                variety = Models.CommentVariety(1)
            elif (variety == "internal") or (variety == '2'):
                variety = Models.CommentVariety(2)
            elif (variety == "activity") or (variety == '3'):
                variety = Models.CommentVariety(3)
            else:
                raise ValueError("Variety not in CommentVariety Enum")
    insert = Models.Comments(ticket=ticket, body=body, created_at=time, created_by=created_by, variety=variety)
    #update = db.session.query(Models.Tickets).filter(Models.Tickets.id == ticket).update({'updated_at':time})
    db.session.add(insert)
    #db.session.add(update)
    db.session.flush()
    details = str(insert.to_dict())
    try:
        log_activity(db, event="Insert", table="comments", item_id=insert.id, details=details, source=created_by)
        act = db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def query_tickets(db, id=None, subject=None, status=None,tags=None,assigned=None,order=None, search=None, sort=None, size=None):
    """Query all tickets with defined filters"""
    # Base Query
    query = db.session.query(Models.Tickets)
    # If looking for specific ticket, return that one
    if id:
        return query.filter(Models.Tickets.id == id).first()
    # get Order
    if order == 'updated_at':
        order = Models.Tickets.updated_at
    elif order == 'created_at':
        order = Models.Tickets.created_at
    elif order == 'assigned':
        order = Models.Tickets.assigned
    elif order == 'priority':
        order = Db.case([
                    (Models.Tickets.priority == 'High', Db.literal_column("'3'")),
                    (Models.Tickets.priority == 'Medium', Db.literal_column("'2'")),
                    (Models.Tickets.priority == 'Low', Db.literal_column("'1'"))
                    ])
    elif order == 'status':
        order = Db.case([
                    (Models.Tickets.status == 'Open', Db.literal_column("'4'")),
                    (Models.Tickets.status == 'Working', Db.literal_column("'3'")),
                    (Models.Tickets.status == 'Waiting', Db.literal_column("'2'")),
                    (Models.Tickets.status == 'Closed', Db.literal_column("'1'"))
                    ])
    else:
        order = Models.Tickets.id
    if sort == 'asc':
        order = order.asc()
    else:
        order = order.desc()
    #If we want to return all matches for any attribute
    if search:
        not_null_filters = []
        not_null_filters.append(Models.Tickets.subject.ilike(f'%{search}%'))
        status = search.capitalize()
        try:
            status = Models.Status[status]
            not_null_filters.append(Models.Tickets.status == status)
        except:
            pass
        tag = db.session.query(Models.Tags).filter(Models.Tags.body.contains(search)).first()
        if tag:
            not_null_filters.append(Models.Tickets.tags.contains(tag))
        user = db.session.query(Models.User).filter(Models.User.username.contains(search)).first()
        if user:
            not_null_filters.append(Models.Tickets.assigned.contains(user))
        if len(not_null_filters) > 0:
            return query.filter(Db.or_(*not_null_filters)).order_by(order).all()
        else:
            return None
    # Add Subject filter
    if subject:
        subject = Models.Tickets.subject.ilike(f'%{subject}%')
        query = query.filter(subject)
    # Add Status filter
    if status:
        status = status.capitalize()
        try:
            status = Models.Status[status]
            query = query.filter(Models.Tickets.status == status)
        except:
            pass
    # Add Assigned filter
    if assigned:
        user = db.session.query(Models.User).filter(Models.User.username.contains(assigned)).first()
        if user:
            assigned = Models.Tickets.assigned.contains(user)
            query = query.filter(assigned)
    # Add Tags filter
    if tags:
        tag = db.session.query(Models.Tags).filter(Models.Tags.body.contains(tags)).first()
        if tag:
            tags = Models.Tickets.tags.contains(tag)
            query = query.filter(tags)
    # Add Size
    if size:
        result = query.order_by(order).limit(int(size))
    # Run Query
    else:
        result = query.order_by(order).all()
    return result

def query_tags(db, tags=None):
    """Query tags, returns list"""
    query = db.session.query(Models.Tags)
    if tags is None:
        return query
    not_null_filters = []
    try:
        tags = tags.split(',')
    except:
        pass
    for tag in tags:
        tag = tag.strip()
        if db.session.query(Models.Tags).filter(Models.Tags.body.is_(tag)).first():
            not_null_filters.append(Models.Tags.body.is_(tag))
    if len(not_null_filters) > 0:
        return query.filter(Db.or_(*not_null_filters)).all()
    else:
        return None

def query_users(db, users=None):
    """Query users, returns list"""
    query = db.session.query(Models.User)
    if users is None:
        return query
    not_null_filters = []
    try:
        users = users.split(',')
    except:
        pass
    for user in users:
        user = user.strip()
        if db.session.query(Models.User).filter(Models.User.username.is_(user)).first():
            not_null_filters.append(Models.User.username.is_(user))
    if len(not_null_filters) > 0:
        return query.filter(Db.or_(*not_null_filters)).all()
    else:
        return None

def query_comments(db, ticket=None,order=None, comment_id=None):
    """Query comments, returns list"""
    if comment_id:
        result = db.session.query(Models.Comments).filter(Models.Comments.id == comment_id).first()
    else:
        if order == 'created_at':
            order = Models.Comments.created_at.desc()
        else:
            order = Models.Comments.id.desc()
        result = db.session.query(Models.Comments).filter(Models.Comments.ticket == ticket).order_by(order).all()
    return result

def query_logs(db, id=None, timestamp=None, event=None, table=None, item_id=None, details=None, source=None, trigger=None):
    """Query Logs, returns list"""
    query = db.session.query(Models.Logs)
    if id:
        return query.filter(Models.Logs.id == id).first()
    if timestamp:
        query = query.filter(Models.Logs.timestamp.ilike(f'%{timestamp}%'))
    if event:
        query = query.filter(Models.Logs.event == event)
    if table:
        query = query.filter(Models.Logs.table == table)
    if item_id:
        query = query.filter(Models.Logs.item_id == item_id)
    if details:
        query = query.filter(Models.Logs.details.ilike(f'%{details}%'))
    if source:
        query = query.filter(Models.Logs.source.ilike(f'%{source}%'))
    if trigger:
        if trigger == "False":
            trigger = 0
        else:
            trigger = 1
        query = query.filter(Models.Logs.trigger == trigger)
    return query.all()

def get_statuses():
    return [status.name for status in Models.Status]

def get_priorities():
    return [priority.name for priority in Models.Priority]

def convert_to_dict(db, items):
    result = []
    try:
        for item in items:
            result.append(item.to_dict())
    except:
        result.append(items.to_dict())
    return result
