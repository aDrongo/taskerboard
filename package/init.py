import modules.database as Db

db = Db.Database('app.db')

Db.insert_user(db, 'admin','admin@contoso.com','taskerboard11@@')
Db.insert_ticket(db,'Init ticket', 'This is your first ticket, check it out!', 1, 1,'system', 'Sample Tag', assigned='admin')
Db.update_ticket(db, id=1, priority=2, user_id='admin')
Db.insert_comment(db,1,'admin','this is the first comment!')