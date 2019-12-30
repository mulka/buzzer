import os
import base64
from base64 import b64decode
from urllib import request, parse
from urllib.parse import parse_qsl

import boto3

from utils import should_auto_buzz


def decrypt(value):
    bytes = boto3.client('kms').decrypt(CiphertextBlob=b64decode(value))['Plaintext']
    return str(bytes, 'utf-8')


TWILIO_SMS_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
TWILIO_ACCOUNT_SID = decrypt(os.environ.get("TWILIO_ACCOUNT_SID"))
TWILIO_AUTH_TOKEN = decrypt(os.environ.get("TWILIO_AUTH_TOKEN"))
MY_NUMBER = decrypt(os.environ.get("MY_NUMBER"))
TWILIO_NUMBER = decrypt(os.environ.get("TWILIO_NUMBER"))


def send_sms(to_number, from_number, body):
    # insert Twilio Account SID into the REST API URL
    populated_url = TWILIO_SMS_URL.format(TWILIO_ACCOUNT_SID)
    post_params = {"To": to_number, "From": from_number, "Body": body}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            read = f.read()
            # print("Twilio returned {}".format(str(read.decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e

    return "SMS sent successfully!"
    

def lambda_handler(event, context):
    print(event)
    params = dict(parse_qsl(event['body']))
    
    if 'CallbackSource' in params and params['CallbackSource'] == 'call-progress-events':
        twiml_response_body = ''
    else:
        twiml_response_body = get_twiml_response_body()
        
    body = f'<Response>{twiml_response_body}</Response>'

    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': body
    }
    
    return response


def get_twiml_response_body():
    if should_auto_buzz():
        body = """
    <Play digits="9"></Play>
        """
        response = send_sms(MY_NUMBER, TWILIO_NUMBER, 'Sending 9')
        # print(response)
    else:
        body = f'<Dial timeout="20"><Number>{MY_NUMBER}</Number></Dial>'
    
    return body


