def convertRequest(data):
    """Convert Query to Dictionary values"""
    dictData = {}
    data = (data.split('/'))[-1]
    data = data.split('&')
    for request in data:
        request = request.split('=')
        dictData[f'{request[0]}'] = f'{request[1]}'
    return dictData