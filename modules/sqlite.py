import sqlite3
from pathlib import Path

from modules.globals import Globals
'''Stolen from HM-A06, don't tell her'''


class SQLite:

    conn = None
    cur = None

    def __init__(self):
        pass

    def connect(self, database):
        Globals.log.debug('Connecting to database ' + database + "...")
        try:
            self.conn = sqlite3.connect(database)
            self.cur = self.conn.cursor()
            Globals.log.debug('Database connection OK')
            return True
        except Exception:
            Globals.log.error('Database connection failed!')
            return False

    def get_cursor(self):
        return self.cur

    def commit(self):
        try:
            self.conn.commit()
            return True
        except Exception:
            Globals.log.error('Database commit failed!')
            return False

    def close(self):
        try:
            self.conn.close()
            return True
        except Exception:
            Globals.log.error('Database disconnect failed!')
            return False