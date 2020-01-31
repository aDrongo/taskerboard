def convertRequest(data):
    dictData = {}
    data = (data.split('/'))[-1]
    data = data.split('&')
    #Process each request
    for request in data:
        request = request.split('=')
        dictData[f'{request[0]}'] = f'{request[1]}'
    return dictData