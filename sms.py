from datetime import datetime, timedelta
from urllib.parse import parse_qsl
import unittest

from pytz import timezone

from utils import get_now, parse_minutes, parse_start_end_times, set_auto_buzz_config, add_auto_buzz_time, get_auto_buzz_times
from exceptions import BuzzerException, NotANumberException


def format_time(t):
    return t.strftime('%-I %p')


def handle_sms(text):
    now = get_now()

    try:
        try:
            minutes = parse_minutes(text)

            add_auto_buzz_time(now, now + timedelta(minutes=minutes))
            set_auto_buzz_config(minutes)
            message = f'Door will be open for the next {minutes} minutes'

        except NotANumberException:
            start, end = parse_start_end_times(text, now)

            add_auto_buzz_time(start, end)
            message = f'Door will be open between {format_time(start)} and {format_time(end)}'

    except BuzzerException as ex:
        message = str(ex)

    return message


def lambda_handler(event, context):

    params = dict(parse_qsl(event['body']))
    
    text = params['Body']
    
    message = handle_sms(text)
    
    body = '<Response>'
    body += '<Message>' + message + '</Message>'
    body += '</Response>'
    response = {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': body
    }
    return response


class HandleSMSTestCase(unittest.TestCase):
    def test_(self):
        print(handle_sms('6-6'))
        # print(handle_sms('10'))
        print(get_auto_buzz_times())
