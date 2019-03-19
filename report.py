from datetime import datetime, time, timedelta
import pymysql


class Report:
    _start_time = time(9, 0)
    _stop_time = time(19, 0)
    expired = 0
    done = 0
    created = 0
    orders = []

    def __init__(self, settings: dict):
        pymysql.install_as_MySQLdb()
        try:
            self._db = pymysql.connect(**settings.get('db', {}))
        except Exception:
            raise ValueError("database settings is bad!")
        self._cursor = self._db.cursor()
        now = datetime.now()
        self.current_time = now.time()
        self.today = now.date()
        if self.today.weekday() in (5, 6):
            self._stop_time = time(16, 0)

    def get_report(self):
        pass

    def get_orders_list(self, created_from, created_to):
        pass

    def _get_from_db(self, created_from, created_to):
        is_successful = self._cursor.execute("""SELECT COUNT(1) FROM suz_orders WHERE
                           coordination=0 AND
                           executor_id=0 AND
                           order_created_datetime > '{}' AND
                           order_created_datetime < '{}'
                           """.format(created_from, created_to))
        self.expired = self._cursor.fetchone()[0] if is_successful else 0
        is_successful = self._cursor.execute("""SELECT COUNT(1) FROM suz_orders WHERE
                           order_created_datetime > '{}' AND
                           order_created_datetime < '{}'
                           """.format(created_to, self.today + self.current_time))
        self.created = self._cursor.fetchone()[0] if is_successful else 0
        is_successful = self._cursor.execute("""SELECT COUNT(1) FROM suz_orders WHERE
                           order_created_datetime > '{}' AND
                           order_created_datetime < '{}' AND
                           coordination!=0""".format(created_to, self.today + self.current_time))
        self.done = self._cursor.fetchone()[0] if is_successful else 0

        if self.expired:
            is_successful = self._cursor.execute("""SELECT id FROM suz_orders WHERE
                           coordination=0 AND
                           executor_id=0 AND
                           order_created_datetime > '{}' AND
                           order_created_datetime < '{}'
                           """.format(created_from, created_to)
            )
            if is_successful > 0:
                self.orders = [i[0] for i in self._cursor.fetchall()]
        self._db.close()

    def at_start_time(self):
        pass

    def at_morning(self):
        pass

    def at_daytime(self):
        pass

    def at_stop_time(self):
        pass
