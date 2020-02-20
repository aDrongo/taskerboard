def convertRequest(data):
    """Convert Query to Dictionary values"""
    dictData = {}
    data = (data.split('/'))[-1]
    data = data.split('&')
    for request in data:
        request = request.split('=')
        if len(request) == 2:
            dictData[f'{request[0]}'] = f'{request[1]}'
    return dictData

def Load_Config(name):
    """Loads the Config file"""
    import json
    config = {}
    parameters = ['mail_server','mail_port','mail_use_tls','mail_use_ssl','mail_debug','mail_username','mail_password','default_mail_sender','notification']
    try:
        with open(f'{name}.json') as f:
            configFile = json.loads(f.read())
        for parameter in parameters:
            config[parameter] = configFile.get(parameter, None)
    except Exception as e:
        print('Config file not loaded')
        raise e
    return config

def query_args(query, *args):
    import re
    queries = {}
    for arg in args:
        queries[arg] = re.sub(f'&?{arg}=.*?(?=&)', '', query)
    return queries

def tags_string(list_items):
    """Convert Tags List to String with comma's"""
    string = ""
    for item in list_items:
        string = string + "," + item.body
    return string[1:]

def parse_hashtags(body):
    """Parse body for hashtags"""
    import re
    result = {}
    hashtags = ['ticket','status','priority','created_by','tags','assigned','due_by']
    for item in hashtags:
        result[item] = re.search(f'#{item}\s\S', body)
    return result


def html_email(message):
    """Format a HTML email with Ticket and Comments"""
    email = f'<html><div style="box-shadow: 0 3px 6px 0 rgba(0,0,0,0.2); padding: 16px; margin: 12px;"><h3>#{message.ticket.id} {message.ticket.subject}</h3>\
    <p>{message.ticket.body}</p>\
    <small><table><tr>\
                <th style="padding: 5px;">Status</th>\
                <th style="padding: 5px;">Priority</th>\
                <th style="padding: 5px;">Assigned</th>\
                <th style="padding: 5px;">Tags</th>\
                <th style="padding: 5px;">Updated at</th>\
                <th style="padding: 5px;">Created at</th>\
                <th style="padding: 5px;">Created by</th>\
                <th style="padding: 5px;">Due</th></tr>\
                <td style="padding: 5px;">{message.ticket.status.name}</td>\
                <td style="padding: 5px;">{message.ticket.priority.name}</td>\
                <td style="padding: 5px;">{message.ticket.assigned}</td>\
                <td style="padding: 5px;">{message.ticket.tags}</td>\
                <td style="padding: 5px;">{message.ticket.updated_at}</td>\
                <td style="padding: 5px;">{message.ticket.created_at}</td>\
                <td style="padding: 5px;">{message.ticket.created_by}</td>\
                <td style="padding: 5px;">{message.ticket.due_by}</td>\
            </table></small></div><hr>'
    for comment in message.comments:
        if comment.variety.name == 'External':
            email = email + f'<div style="box-shadow: 0 3px 6px 0 rgba(0,0,0,0.2); padding: 16px; margin: 12px;"><p>{comment.body}<p>\
            <small>{comment.created_by} at {comment.created_at}</small></div><hr>'
        elif comment.variety.name == 'Activity':
            email = email + f'<div style="box-shadow: 0 3px 6px 0 rgba(0,0,0,0.2); padding: 16px; margin: 12px;"><small>{comment.body} by {comment.created_by} at {comment.created_at}</small></div><hr>'
    email = email + "</html>"
    return email