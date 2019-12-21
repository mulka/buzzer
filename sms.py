from urllib.parse import parse_qsl


from utils import set_auto_buzz_config


def lambda_handler(event, context):

    params = dict(parse_qsl(event['body']))
    
    text = params['Body']
    
    try:
        minutes = int(text)
    except ValueError:
        minutes = 0
        
    if 5 <= minutes <= 60:
        set_auto_buzz_config(minutes)
        message = f'Door will be open for the next {minutes} minutes'
    else:
        message = 'Please type a number between 5 and 60'
    
    body = '<Response>'
    body += '<Message>' + message + '</Message>'
    body += '</Response>'
    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': body
    }
    return response
