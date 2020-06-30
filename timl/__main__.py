import argparse
import requests
from os.path import expanduser
from datetime import datetime
from .utils import read_config, convert_date, round_seconds, get_time, time_diff_seconds, time_diff_human
from .queries import (
    get_last_log,
    get_today_log,
    get_unpushed_log,
    add_log,
    delete_log,
    update_log_endtime,
    update_log_pushed,
    create_log_table,
    get_conn,
)

CONFIG_PATH = '~/.timl.yml'

TOTAL_DAY_SECONDS = 21600  # 6hrs

# COLORS
COLOR_DARK_GREY = '\033[90m'
COLOR_BLUE = '\033[34m'
COLOR_RED = '\033[31m'
COLOR_RESET = '\033[0m'


def get_tasks(jira_url, username, api_key):
    """Get all assigned subtasks which are not done"""
    url = jira_url + '/rest/api/3/search'
    params = {
        'jql': 'assignee = currentUser() AND issuetype in subtaskIssueTypes() and status != done'
    }
    response = requests.get(url, params=params, auth=(username, api_key))
    if not response.ok:
        raise ValueError("error: failed to get assigned tasks")
    response_json = response.json()
    issues = response_json['issues']
    return [(issue['key'], issue['fields']['summary']) for issue in issues]

def push_log(conn, jira_url, username, api_key):
    """Push all (not already pushed) logs to jira"""
    stop_task(conn)
    rows = get_unpushed_log(conn)
    if not rows:
        print("Nothing to push")
    else:
        for (id_, task, start_time, end_time) in rows:
            seconds = time_diff_seconds(start_time, end_time)
            time_spent = round_seconds(seconds)
            start_time = convert_date(start_time)
            url = '{0}/rest/api/3/issue/{1}/worklog'.format(jira_url, task)
            data = {
                'started': start_time,
                'timeSpentSeconds': time_spent,
            }
            response = requests.post(url, json=data, auth=(username, api_key))
            if response.ok:
                # TODO: single sql UPDATE for all logs
                update_log_pushed(conn, id_)
                print("Pushed work log for {0}: {1}".format(task, time_diff_human(seconds)))
            else:
                print("{color_start}error: failed to push logs for {task} - {status_code}: {error_text}{color_end}"
                      .format(color_start=COLOR_RED,
                              color_end=COLOR_RESET,
                              task=task,
                              status_code=response.status_code,
                              error_text=response.text)
                )

def clear_log(conn, task):
    """Clear the logs"""
    delete = task or 'all'
    confirm = input('Are you sure you want to clear logs for {0}? [y/n]: '.format(delete))
    if confirm.lower() == 'y':
        delete_log(conn, task)
        print("Deleted logs for {0}".format(delete))
    else:
        print('Nothing deleted')

def stop_task(conn):
    """Stop time logging for the current task"""
    time_now = datetime.utcnow()
    row = get_last_log(conn)
    if row:
        id_, _, start_time, end_time = row
        if not end_time:
            update_log_endtime(conn, id_=id_, end_time=time_now)

def start_task(conn, task):
    """Start time logging for the given task"""
    if not task:
        raise ValueError("error: task is required when using start")
    time_now = datetime.utcnow()
    # update the end time of the last item in the logs
    row = get_last_log(conn)
    if row:
        id_, _, start_time, end_time = row
        if not end_time:
            update_log_endtime(conn, id_=id_, end_time=time_now)
    # add a new item in the logs
    add_log(conn, task.upper(), start_time=time_now)

def get_active_task(conn):
    """Get the current active task"""
    task = None
    row = get_last_log(conn)
    if row:
        _, last_task, _, end_time = row
        if not end_time:
            task = last_task
    return task

def get_status(conn):
    """Get the status of the current task"""
    status = "No task"
    row = get_last_log(conn)
    if row:
        _, task, start_time, end_time = row
        if not end_time:
            time_now = datetime.utcnow()
            diff_seconds = time_diff_seconds(start_time, time_now)
            diff = time_diff_human(diff_seconds)
            status = "{0} for {1}".format(task, diff)
    return status

def get_log(conn):
    """Get all logs for today"""
    active_task = get_active_task(conn)
    rows = get_today_log(conn)
    if not rows:
        output = "Nothing logged today"
    else:
        items = []
        total_time = 0
        for (pushed, task, start_time, end_time) in rows:
            if not end_time:
                end_time = datetime.utcnow()
            duration = time_diff_seconds(start_time, end_time)
            start_time = get_time(start_time)
            total_time += duration
            is_active_task = task == active_task
            items.append("{color_start}{task} @ {time} for {duration}{color_end}".format(
                color_start=COLOR_BLUE if is_active_task else COLOR_DARK_GREY if pushed else '',
                color_end=COLOR_RESET if is_active_task or pushed else '',
                task=task,
                time=start_time,
                duration=time_diff_human(duration),
            ))
        time_percent = total_time / TOTAL_DAY_SECONDS * 100
        output = "Logged today ({0} - {1:.0f}%):\n{2}".format(time_diff_human(total_time),
                                                             time_percent, '\n'.join(items))
    return output

def get_summary(conn):
    """Get summary for today"""
    active_task = get_active_task(conn)
    rows = get_today_log(conn)
    if not rows:
        output = "Nothing logged today"
    else:
        logs = {}
        for (_, task, start_time, end_time) in rows:
            if not end_time:
                end_time = datetime.utcnow()
            diff_seconds = time_diff_seconds(start_time, end_time)
            if logs.get(task) is None:
                logs[task] = []
            logs[task].append(diff_seconds)
        items = []
        total_time = 0
        for task, times in sorted(logs.items()):
            duration = sum(times)
            total_time += duration
            is_active_task = task == active_task
            items.append("{color_start}{task}: {duration}{color_end}".format(
                color_start=COLOR_BLUE if is_active_task else '',
                color_end=COLOR_RESET if is_active_task else '',
                task=task,
                duration=time_diff_human(duration),
            ))
        time_percent = total_time / TOTAL_DAY_SECONDS * 100
        output = "Logged today ({0} - {1:.0f}%):\n{2}".format(time_diff_human(total_time),
                                                             time_percent, '\n'.join(items))
    return output

def parse_args():
    parser = argparse.ArgumentParser("JIRA Time Logger")
    parser.add_argument('command',
                        choices=['status', 'log', 'summary', 'start', 'stop', 'clear', 'push', 'tasks'],
                        help="The command to run.")
    parser.add_argument('task',
                        nargs='?',
                        help="The task to apply the command to. Only required when using the start or clear commands.")
    return parser.parse_args()

def run():
    config = read_config(expanduser(CONFIG_PATH))
    db_path = expanduser(config['db_path'])
    url = config['jira_url']
    username = config['jira_username']
    api_key = config['jira_api_key']

    conn = get_conn(db_path)
    create_log_table(conn)

    args = parse_args()
    if args.command == 'status':
        status = get_status(conn)
        print(status)
    elif args.command == 'start':
        start_task(conn, args.task)
        print("Working on {0}".format(args.task))
    elif args.command == 'stop':
        stop_task(conn)
        print("Twiddling thumbs")
    elif args.command == 'log':
        logs = get_log(conn)
        print(logs)
    elif args.command == 'summary':
        summary = get_summary(conn)
        print(summary)
    elif args.command == 'clear':
        clear_log(conn, args.task)
    elif args.command == 'push':
        push_log(conn, url, username, api_key)
    elif args.command == 'tasks':
        tasks = get_tasks(url, username, api_key)
        for task, description in tasks:
            print("{0}: {1}".format(task, description))
    else:
        raise ValueError("error: unsupported command")

    conn.commit()

def main():
    try:
        run()
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()
