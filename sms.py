import time
from urllib.parse import parse_qsl

import boto3

def lambda_handler(event, context):

    params = dict(parse_qsl(event['body']))
    
    text = params['Body']
    
    try:
        mins = int(text)
    except:
        mins = 0
        
    if 5 <= mins <= 60:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table('apartment-buzzer-auto-buzz')
        response = table.update_item(
            Key={
                'key': 'auto-buzz'
            },
            UpdateExpression='SET #until = :until',
            ExpressionAttributeNames={
                '#until': 'until'
            },
            ExpressionAttributeValues={
                ':until': int(time.time() + 60*mins)
            }
        )
        message = f'Door will be open for the next {mins} minutes'
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