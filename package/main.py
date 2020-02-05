import os
from flask import Flask, render_template, Response, redirect, url_for, request
from datetime import datetime
import modules.database as db

#print(dir(db.session.query()))

db.insert_user('ben.gardner','ben.gardner@nwmsrocks.com','1234')
db.insert_user('test.uuser','test@nwmsrocks.com','4444')
#print(db.check_password('ben.gardner','1244'))

#update_user('ben.gardner', 'test.user', 'test@nwmsrocks.com')

#delete_user('test.user')

db.insert_ticket('test ticket', 'this is a test6', 2,'tester')
db.insert_ticket('test ticket2', 'this is a test5', 2,'tester')
db.insert_ticket('test ticket3', 'this is a test4', 2,'tester')
db.insert_ticket('test ticket4', 'this is a test3', 2,'tester')
db.insert_ticket('test ticket5', 'this is a test2', 2,'tester')
db.insert_ticket('test ticket6', 'this is a test1', 2,'tester')
db.insert_ticket('test ticket', 'this is a test', 2,'tester',1,'project')
db.insert_ticket('test ticket2', 'this is a test', 2,'tester',1,'project')
db.insert_ticket('test ticket3', 'this is a test', 2,'tester',1,'project')
db.insert_ticket('test ticket', 'this is a test', 2,'tester',1,'project')
db.insert_ticket('test ticket2', 'this is a test', 2,'tester',1,'project')
db.insert_ticket('test ticket3', 'this is a test', 2,'tester',1,'project')

#db.update_ticket(1, 1,'tested','this test is complete', 1, 'tester')
#db.update_ticket(7, 1, "1415151", "15", 2, "test.user", None, "Ticket", None)
db.insert_comment(1,'ben.gardner','this is the first test comment')
db.insert_comment(1,'ben.gardner','this is a second test comment')
db.insert_comment(2,'ben.gardner','this is another test comment')
db.insert_comment(1,'ben.gardner','this is the 1first test comment')
db.insert_comment(1,'ben.gardner','this is a 1second test comment')
db.insert_comment(2,'ben.gardner','this is 1another test comment')

#result = db.query_comments(1)
#for item in result:
    #body, created_at, created_by, id, ticket
#    print(item.body)
