import modules.database as Db
import modules.assorted as Assorted

class Mail():
    """Connects and processes Mail"""

    def __init__(self, config):
        """Initialize"""
        from imapclient import IMAPClient
        self.mail_username = config['mail_username']
        self.mail_password = config['mail_password']
        self.mail_server = config['mail_server']
        self.mail_connection = IMAPClient(self.mail_server, use_uid=True)

    def get_mail(self):
        """Connect to mailbox and retrieve messages to mail list"""
        import pyzmail
        with self.mail_connection as c:
            self.mail = []
            c.login(f'{self.mail_username}',f'{self.mail_password}')
            c.select_folder('INBOX', readonly=True)
            UIDs = c.search(['ALL'])
            #Figure out what mail i want to get
            UIDs = UIDs[-5:]
            print(UIDs)
            for UID in UIDs:
                messages = c.fetch(UID, ['Body[]', 'FLAGS'])
                message = messages[list(messages)[0]][b'BODY[]']
                pyzmessage = pyzmail.PyzMessage.factory(message)
                try:
                    msg = Message()
                    msg.uid = UID
                    msg.from_address = pyzmessage.get_address('from')[1]
                    msg.from_user = pyzmessage.get_address('from')[0]
                    msg.cc = pyzmessage.get_addresses('cc')
                    msg.subject = pyzmessage.get_subject()
                    msg.body = pyzmessage.html_part.get_payload().decode('UTF-8')
                    self.mail.append(msg)
                except Exception as e:
                    print(e)
        
    def process_mail(self, db):
        """Loop through messages and insert a new ticket or comment"""
        results = {}
        for msg in self.mail:
            #Parse mail
            hash_tags = Assorted.parse_hashtags(msg.body)
            #if no ticket identified create new ticket
            if "#Ticket" not in msg.subject:
                results[msg.uid] = Db.insert_ticket(db, 
                                                    subject=msg.subject,
                                                    body=msg.body,
                                                    status=hash_tags.get('status', None),
                                                    priority=hash_tags.get('priority', None),
                                                    created_by=hash_tags.get('created_by', None),
                                                    tags=hash_tags.get('tags', None),
                                                    assigned=hash_tags.get('assigned', None),
                                                    due_by=hash_tags.get('due_by', None)
                                                    )
            else:
                #if ticket identified then add comment
                ticket_id = hash_tags.get('ticket', None)
                if ticket_id:
                    results[msg.uid] = Db.insert_comment(db, ticket=ticket_id, created_by=msg.from_address, body=msg.body)
                else:
                    results[msg.uid] = False
        return results


class Message():
    """Holds Mail Message Details"""
    uid = None
    from_address = None
    from_user = None
    cc = None
    subject = None
    body = None
    ticket = None

    def __repr__(self):
        return f'{self.uid}'