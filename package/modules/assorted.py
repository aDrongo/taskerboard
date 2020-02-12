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

def Load_Config():
    """Loads the Config file"""
    import json
    config = {}
    parameters = ['mail_server','mail_port','mail_use_tls','mail_use_ssl','mail_debug','mail_username','mail_password','default_mail_sender']
    try:
        with open('config.json') as f:
            configFile = json.loads(f.read())
        for parameter in self.parameters:
            try:
                config[parameter] = configFile[parameter]
            except Exception as e:
                print(parameter + 'failed to load')
    except Exception as e:
        print('Config file not loaded')
        raise e
    return config

def query_args(query, *args):
    import re
    queries = {}
    for arg in args:
        queries[arg] = re.sub(f'&?{arg}=.*(?=&)*', '', query)
    return queries

def tags_string(list_items):
    """Convert Tags List to String with comma's"""
    string = ""
    for item in list_items:
        string = string + "," + item.body
    return string[1:]