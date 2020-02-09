import os
from flask import Flask, render_template, Response, redirect, url_for, request
from datetime import datetime
import modules.database as Db

db = Db.Database('app.db')

Db.insert_user(db, 'sample.user','sample.user@contoso.com','1234')
Db.insert_user(db, 'tester','test@contoso.com','4444')

Db.insert_ticket(db,'Printer Toner Low', 'Printer Toner at Location 241 is running low', 3, 1,'tester', 'Toner, Printer')
Db.insert_ticket(db,'Server slow', 'Server has exceded IOPS warning threshold', 3, 1, 'tester', 'Server')
Db.insert_ticket(db,'Risky Signin', 'The user "customer" logged in from an unknown location', 3, 1, 'tester')
Db.insert_ticket(db,'Documents Request', 'Please send us these Documents, A, B, C, D', 2, 1, 'tester')
Db.insert_ticket(db,'This is some random', 'this is some random ticket with information in it', 2, 1, 'tester')
Db.insert_ticket(db,'test ticket6', 'this is a test1', 2, 1, 'tester', assigned='tester')
Db.insert_ticket(db,'test ticket', 'this is a test', 4, 1, 'tester',)
Db.insert_ticket(db,'test ticket2', 'this is a test', 1, 3, 'tester')
Db.insert_ticket(db,'test ticket3', 'this is a test', 2, 3, 'tester')
Db.insert_ticket(db,'test ticket', 'this is a test', 2, 3, 'tester')
Db.insert_ticket(db,'test ticket2', 'this is a test', 2, 2, 'tester')
Db.insert_ticket(db,'test ticket3', 'this is a test', 2, 2,'tester')

Db.insert_comment(db,1,'tester','this is the first test comment')
Db.insert_comment(db,1,'tester','this is a second test comment')
Db.insert_comment(db,2,'tester','this is another test comment')
Db.insert_comment(db,1,'tester','this is the 1first test comment')
Db.insert_comment(db,1,'tester','this is a 1second test comment')
Db.insert_comment(db,2,'tester','this is 1another test comment')

#action=query_tickets&tags=tick
#action=update_ticket&ticket=1&subject='API test'&body='This is a test of the API'&status=Working