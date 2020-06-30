import sqlite3

def get_unpushed_log(conn):
    """Get all logs that aren't pushed"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, start_time, end_time FROM timelogs WHERE pushed = 0")
    rows = cursor.fetchall()
    return rows

def get_today_log(conn):
    """Get all logs for today"""
    cursor = conn.cursor()
    cursor.execute("SELECT pushed, task, start_time, end_time FROM timelogs WHERE start_time>=date('now', 'start of day')")
    rows = cursor.fetchall()
    return rows

def get_last_log(conn):
    """Get the last item in the time logs"""
    cursor = conn.cursor()
    cursor.execute('SELECT id, task, start_time, end_time FROM timelogs ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    return row

def update_log_pushed(conn, id_):
    """Update the pushed status of the given item in the time logs"""
    cursor = conn.cursor()
    cursor.execute('UPDATE timelogs SET pushed = 1 WHERE id = ?;', (id_,))

def update_log_endtime(conn, id_, end_time):
    """Update the given item in the time logs with the given end_time"""
    cursor = conn.cursor()
    cursor.execute('UPDATE timelogs SET end_time = ? WHERE id = ?;', (end_time, id_))

def add_log(conn, task, start_time):
    """Add a new item to the time logs"""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO timelogs (task, start_time) VALUES (?, ?);', (task, start_time))

def delete_log(conn, task):
    """Delete all logs or logs for the given task"""
    cursor = conn.cursor()
    if task:
        cursor.execute('DELETE FROM timelogs WHERE task = ?;', (task,))
    else:
        cursor.execute('DELETE FROM timelogs')

def create_log_table(conn):
    """Create the log table if it does not exist"""
    query = """CREATE TABLE IF NOT EXISTS timelogs (
        id integer PRIMARY KEY,
        pushed integer NOT NULL DEFAULT 0,
        task text NOT NULL,
        start_time text NOT NULL,
        end_time text
    );"""
    cursor = conn.cursor()
    cursor.execute(query)

def get_conn(db_path):
    """Get the connection to the db"""
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as ex:
        print(ex)
        raise ValueError('error: failed to connect to db')
    return conn
