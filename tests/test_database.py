import sys 
sys.path.append('..')
import os
import pytest

import package.modules.database as Db

@pytest.fixture(scope="module")
def database():
    """Our setup of test database and teardown once finished"""
    db = Db.Database('test.db')
    yield db 
    os.remove('test.db')

def test_insert_user(database):
    Db.insert_user(database, 'test', 'test@contoso.com', '1234')
    Db.insert_user(database, 'tester', 'tester@contoso.com', '1234')
    Db.insert_user(database, 'testing', 'someone@contoso.com', '1234')
    user = Db.query_users(database, 'test')
    assert user[0].username == 'test'
    assert user[0].email == 'test@contoso.com'

def test_check_password(database):
    assert Db.check_password(database, 'test', '1234')

def test_update_user(database):
    Db.update_user(database, 'test', 'different@contoso.com', '5678')
    user = Db.query_users(database, 'test')
    assert user[0].email == 'different@contoso.com'
    assert Db.check_password(database, 'test', '5678')

def test_delete_user(database):
    user = Db.query_users(database, 'testing')[0]
    assert user.username == 'testing'
    assert Db.delete_user(database, 'testing') == True
    assert Db.query_users(database, 'testing') == None

def test_insert_tags(database):
    Db.insert_tags(database, 'test')
    tags = Db.query_tags(database, 'test')
    assert tags[0].body == 'test'

def test_insert_multiple_tags(database):
    Db.insert_tags(database, 'tester,testing')
    tags = Db.query_tags(database, 'testing')
    assert tags[0].body == 'testing'

def test_insert_ticket(database):
    #Create a default ticket with integers for enumerators
    ticket = Db.insert_ticket(database, subject='Subject test', body='body of a test', status=1, priority=1, created_by='test', assigned='test', tags='taggit')
    assert ticket == True
    #If ID specified should return only that one ticket
    ticket = Db.query_tickets(database, id=1)
    assert ticket.subject == 'Subject test'
    assert ticket.tags[0].body == 'taggit'
    #Create another ticket with strings for enumerators
    ticket = Db.insert_ticket(database, subject='Subject another', body='body of second test', status='Open', priority='High', created_by='test', assigned='test', tags='tagger,tagging')
    assert ticket == True
    ticket = Db.query_tickets(database, subject='Subject another')
    #Check everything was inserted
    assert ticket[0].subject == 'Subject another'
    assert ticket[0].body == 'body of second test'
    assert ticket[0].tags[0].body in ('tagger','tagging')
    assert ticket[0].tags[1].body in ('tagger','tagging')
    assert ticket[0].assigned[0].username == 'test'
    assert ticket[0].created_by == 'test'
    assert ticket[0].status.name == 'Open'

def test_update_ticket(database):
    ticket = Db.update_ticket(database, id=1, subject='Updated subject', body='body', status=2, priority=2, created_by='tester', assigned='tester', tags='updated')
    assert ticket == True
    ticket = Db.query_tickets(database, id=1)
    assert ticket.subject == 'Updated subject'
    assert ticket.body == 'body'
    assert ticket.status.value == 2
    assert ticket.priority.value == 2
    assert ticket.created_by == 'tester'
    assert ticket.assigned[0].username == 'tester'
    assert ticket.tags[0].body == 'updated'

def test_insert_comment(database):
    result = Db.insert_comment(database, 1, 'test', 'comment')
    assert result == True
    Db.insert_comment(database, 1, 'test', 'second comment')
    result = Db.query_comments(database, 1)
    assert result[1].body == 'comment'
    assert result[0].body == 'second comment'

def test_convert_to_dict(database):
    ticket = Db.query_tickets(database, id=1)
    result = Db.convert_to_dict(database, ticket)
    assert result[0].get('id') == 1