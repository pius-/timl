import yaml
from datetime import datetime

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 86400

TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
DATETIME_FORMAT_JIRA = '%Y-%m-%dT%H:%M:%S.%f'

def read_config(config_path):
    """Read config file into a dict"""
    with open(config_path, 'r') as config_file:
        config = yaml.full_load(config_file)
    return config

def round_seconds(seconds):
    """Round up seconds to multiple of 60 seconds"""
    rounded = - (-seconds//SECONDS_IN_MINUTE) * SECONDS_IN_MINUTE
    return rounded

def convert_date(date):
    """Convert a date string into and ISO 8601 date string"""
    date_obj = datetime.strptime(date, DATETIME_FORMAT)
    date_str = datetime.strftime(date_obj, DATETIME_FORMAT_JIRA)[:-3] + '+0000'
    return date_str

def get_time(date):
    """Get the time from a datetime string"""
    date_obj = datetime.strptime(date, DATETIME_FORMAT)
    time = date_obj.strftime(TIME_FORMAT)
    return time

def time_diff_seconds(start_time, end_time):
    """Return time difference in seconds"""
    if not isinstance(start_time, datetime):
        start_time = datetime.strptime(start_time, DATETIME_FORMAT)
    if not isinstance(end_time, datetime):
        end_time = datetime.strptime(end_time, DATETIME_FORMAT)
    time_diff = end_time - start_time
    return time_diff.seconds

def time_diff_human(diff_seconds):
    """Return a human readable time difference"""
    days = diff_seconds // SECONDS_IN_DAY
    hours = diff_seconds % SECONDS_IN_DAY // SECONDS_IN_HOUR
    minutes = diff_seconds % SECONDS_IN_HOUR // SECONDS_IN_MINUTE
    seconds = diff_seconds % SECONDS_IN_MINUTE
    summary = []
    if days > 0:
        summary.append("{0} day{1}".format(days, '' if days == 1 else 's'))
    if hours > 0:
        summary.append("{0} hr{1}".format(hours, '' if hours == 1 else 's'))
    if minutes > 0:
        summary.append("{0} min{1}".format(minutes, '' if minutes == 1 else 's'))
    if summary:
        output = ', '.join(summary)
    else:
        output = "{0} sec{1}".format(seconds, '' if seconds == 1 else 's')
    return output
