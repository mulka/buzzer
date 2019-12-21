from time import time
import unittest

import boto3


def get_auto_buzz_config():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('apartment-buzzer-auto-buzz')

    response = table.get_item(
        Key={
            'key': 'auto-buzz'
        }
    )

    try:
        rv = response['Item']
    except KeyError:
        rv = None

    return rv


def _should_auto_buzz(config):
    auto_buzz = False

    try:
        value = config['value']
        until = config['until']

        if value == 'true' and until > time():
            auto_buzz = True
    except KeyError:
        pass

    return auto_buzz


def should_auto_buzz():
    config = get_auto_buzz_config()

    return _should_auto_buzz(config)


class AutoBuzzTestCase(unittest.TestCase):
    def test_auto_buzz_true(self):
        config = {
            'value': 'true',
            'until': time() + 1
        }
        auto_buzz = _should_auto_buzz(config)
        self.assertTrue(auto_buzz)

    def test_auto_buzz_false(self):
        config = {
            'value': 'true',
            'until': time() - 1
        }
        auto_buzz = _should_auto_buzz(config)
        self.assertFalse(auto_buzz)