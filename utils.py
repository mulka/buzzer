import uuid
from time import time, sleep
import unittest
from datetime import datetime, timedelta

import boto3
from pytz import timezone

from exceptions import BuzzerException, NotANumberException


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('apartment-buzzer-auto-buzz')
times_table = dynamodb.Table('apartment-buzzer-auto-buzz-times')


def get_now():
    return datetime.now(timezone('US/Eastern'))


def parse_minutes(text):
    try:
        minutes = int(text)
    except ValueError:
        raise NotANumberException()
    if not 5 <= minutes <= 60:
        raise BuzzerException('Please type a number between 5 and 60')

    return minutes


def parse_start_end_times(text, now):
    start, end = text.split('-')
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        start = 0
        end = 0

    if not 1 <= start <= 12 or not 1 <= end <= 12:
        raise BuzzerException('Hours need to be between 1 and 12')
    else:
        start_dt = now.replace(hour=start, minute=0, second=0, microsecond=0)
        end_dt = now.replace(hour=end, minute=0, second=0, microsecond=0)
        while now >= start_dt:
            start_dt += timedelta(hours=12)
        while start_dt >= end_dt:
            end_dt += timedelta(hours=12)

    return start_dt, end_dt


def add_auto_buzz_time(start, end):
    start = start.isoformat()
    end = end.isoformat()
    times_table.put_item(
        Item={
            'uuid': str(uuid.uuid4()),
            'start': start,
            'end': end,
        }
    )


def get_auto_buzz_times():
    response = times_table.scan()

    return response['Items']


def set_auto_buzz_config(minutes):
    response = table.update_item(
        Key={
            'key': 'auto-buzz'
        },
        UpdateExpression='SET #until = :until',
        ExpressionAttributeNames={
            '#until': 'until'
        },
        ExpressionAttributeValues={
            ':until': int(time() + 60 * minutes)
        }
    )


def get_auto_buzz_config():
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


def _should_auto_buzz_times(times):
    now = get_now()

    for time_entry in times:
        if datetime.fromisoformat(time_entry['start']) < now < datetime.fromisoformat(time_entry['end']):
            return True
    return False


def should_auto_buzz():
    config = get_auto_buzz_config()
    times = get_auto_buzz_times()

    return _should_auto_buzz(config) or _should_auto_buzz_times(times)


class StartEndTimesTestCase(unittest.TestCase):
    def test_parse_start_end_times(self):
        now = datetime(2019, 1, 1, 0)

        text = '1-2'
        start, end = parse_start_end_times(text, now)

        self.assertEqual(start, datetime(2019, 1, 1, 1))
        self.assertEqual(end, datetime(2019, 1, 1, 2))

    def test_parse_start_end_times_pm_to_am(self):
        now = datetime(2019, 1, 1, 20)

        text = '6-8'
        start, end = parse_start_end_times(text, now)

        self.assertEqual(start, datetime(2019, 1, 2, 6))
        self.assertEqual(end, datetime(2019, 1, 2, 8))

    def test_parse_start_end_times_am_to_pm(self):
        now = datetime(2019, 1, 1, 8)

        text = '6-7'
        start, end = parse_start_end_times(text, now)

        self.assertEqual(start, datetime(2019, 1, 1, 18))
        self.assertEqual(end, datetime(2019, 1, 1, 19))

    def test_parse_start_end_times_start_now(self):
        now = datetime(2019, 1, 1, 1)

        text = '1-2'
        start, end = parse_start_end_times(text, now)

        self.assertEqual(start, datetime(2019, 1, 1, 13))
        self.assertEqual(end, datetime(2019, 1, 1, 14))

    def test_parse_start_end_times_invalid(self):
        now = datetime(2019, 1, 1, 0)

        text = '1-50'

        with self.assertRaises(BuzzerException) as context:
            parse_start_end_times(text, now)


class AutoBuzzTestCase(unittest.TestCase):
    def test_auto_buzz_true(self):
        config = {
            'value': 'true',
            'until': time() + 60
        }
        auto_buzz = _should_auto_buzz(config)
        self.assertTrue(auto_buzz)

    def test_auto_buzz_false(self):
        config = {
            'value': 'true',
            'until': time() - 60
        }
        auto_buzz = _should_auto_buzz(config)
        self.assertFalse(auto_buzz)

    def test_in_range(self):
        times = [
            {'start': time() - 60, 'end': time() + 60}
        ]

        auto_buzz = _should_auto_buzz_times(times)
        self.assertTrue(auto_buzz)

    def test_out_of_range(self):
        times = [
            {'start': time() - 60, 'end': time() - 1}
        ]

        auto_buzz = _should_auto_buzz_times(times)
        self.assertFalse(auto_buzz)


if __name__ == '__main__':
    add_auto_buzz_time(get_now(), get_now() + timedelta(seconds=1))
    print(should_auto_buzz())
    sleep(2)
    print(should_auto_buzz())

