import os
from flask import Flask, render_template, Response, redirect, url_for, request
from datetime import datetime
import modules.database as Db

#print(dir(Db.session.query()))

Db.insert_user('ben.gardner','ben.gardner@nwmsrocks.com','1234')
Db.insert_user('tester','test@nwmsrocks.com','4444')
#print(Db.check_password('ben.gardner','1244'))

#update_user('ben.gardner', 'test.user', 'test@nwmsrocks.com')

#delete_user('test.user')

Db.insert_ticket('test ticket', 'this is a test6', 2,'tester')
Db.insert_ticket('test ticket2', 'this is a test5', 2,'tester')
Db.insert_ticket('test ticket3', 'this is a test4', 2,'tester')
Db.insert_ticket('test ticket4', 'this is a test3', 2,'tester')
Db.insert_ticket('test ticket5', 'this is a test2', 2,'tester')
Db.insert_ticket('test ticket6', 'this is a test1', 2,'tester', assigned='ben.gardner')
Db.insert_ticket('test ticket', 'this is a test', 2,'tester',1,'project')
Db.insert_ticket('test ticket2', 'this is a test', 2,'tester',1,'project')
Db.insert_ticket('test ticket3', 'this is a test', 2,'tester',1,'project')
Db.insert_ticket('test ticket', 'this is a test', 2,'tester',1,'project')
Db.insert_ticket('test ticket2', 'this is a test', 2,'tester',1,'project')
Db.insert_ticket('test ticket3', 'this is a test', 2,'tester',1,'project')

#Db.update_ticket(1, 1,'tested','this test is complete', 1, 'tester')
#Db.update_ticket(7, 1, "1415151", "15", 2, "test.user", None, "Ticket", None)
Db.insert_comment(1,'ben.gardner','this is the first test comment')
Db.insert_comment(1,'ben.gardner','this is a second test comment')
Db.insert_comment(2,'ben.gardner','this is another test comment')
Db.insert_comment(1,'ben.gardner','this is the 1first test comment')
Db.insert_comment(1,'ben.gardner','this is a 1second test comment')
Db.insert_comment(2,'ben.gardner','this is 1another test comment')
#result = Db.query_comments(1)
#for item in result:
    #body, created_at, created_by, id, ticket
#    print(item.body)


users = Db.db.session.query(Db.User).filter(Db.User.username.in_(['ben.gardner'])).all()
ticket = Db.db.session.query(Db.Tickets).filter(Db.Tickets.id == 1).first()
ticket.assigned = [user for user in users]


Db.db.session.commit()

tag = Db.Tags()
tag.body = 'Tick'
Db.db.session.add(tag)

tag = Db.Tags()
tag.body = 'Test'
Db.db.session.add(tag)

Db.db.session.commit()

tags = Db.db.session.query(Db.Tags).filter(Db.Tags.body.in_(['Tick'])).all()
tags = tags + Db.db.session.query(Db.Tags).filter(Db.Tags.body.in_(['Test'])).all()
ticket = Db.db.session.query(Db.Tickets).filter(Db.Tickets.id == 1).first()
ticket.tags = [tag for tag in tags]


Db.db.session.commit()