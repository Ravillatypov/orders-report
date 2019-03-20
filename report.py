from datetime import datetime, time, timedelta
import pymysql

MINI_REPORT = """
скоординировано   {s.done}
создано           {s.created}
просрочено        {s.expired}"""

START_REPORT = """Доброе утро!
количество заявок созданных за ночь: {}"""

ORDERS_REPORT = """[order {0}](https://site.com/orders/{0})"""


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
            self._db = pymysql.connect(**settings)
        except Exception:
            raise ValueError("database settings is bad!")
        self._cursor = self._db.cursor()
        now = datetime.now()
        t = now.time()
        self.current_time = time(t.hour, t.minute)
        self.today = now.date()
        yesterday = now - timedelta(days=1)
        self.night = datetime(
            yesterday.year, yesterday.month, yesterday.day, 19)
        self.yesterday = yesterday
        self.today_at5 = datetime(now.year, now.month, now.day, 5)
        self.ten_minutes_ago = now - timedelta(minutes=10)
        if self.today.weekday() in (5, 6):
            self._stop_time = time(16, 0)

    def get_mini_report(self):
        return MINI_REPORT.format(s=self)

    def get_orders_report(self):
        result = ""
        for i in self.orders:
            result += ORDERS_REPORT.format(i)
        return result

    def get_report(self):
        if self .current_time < self._start_time or self.current_time > self._stop_time:
            return ""
        if self.current_time == self._start_time:
            return self.at_start_time()
        if self.current_time == self._stop_time:
            return self.at_stop_time()
        if self.current_time <= time(10, 1):
            return self.at_morning()
        return self.at_daytime()

    def _get_counts_from_db(self, created_from, created_to):
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
                           """.format(created_to, datetime.now()))
        self.created = self._cursor.fetchone()[0] if is_successful else 0
        is_successful = self._cursor.execute("""SELECT COUNT(1) FROM suz_orders WHERE
                           order_created_datetime > '{}' AND
                           order_created_datetime < '{}' AND
                           coordination!=0""".format(created_to, datetime.now()))
        self.done = self._cursor.fetchone()[0] if is_successful else 0

    def _get_orders_from_db(self, created_from, created_to):
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
        self._get_counts_from_db(self.night, self.night)
        self._db.close()
        return START_REPORT.format(self.created)

    def at_morning(self):
        self._get_counts_from_db(self.today_at5, self.ten_minutes_ago)
        self._get_orders_from_db(self.today_at5, self.ten_minutes_ago)
        return "за посление 10 минут:\n" + self.get_mini_report() + self.get_orders_report()

    def at_daytime(self):
        self._get_counts_from_db(self.night, self.ten_minutes_ago)
        self._get_orders_from_db(self.night, self.ten_minutes_ago)
        return "за посление 10 минут:\n" + self.get_mini_report() + self.get_orders_report()

    def at_stop_time(self):
        self._get_counts_from_db(self.yesterday, self.yesterday)
        self._get_orders_from_db(self.yesterday, self.yesterday)
        return "за день:\n" + self.get_mini_report() + self.get_orders_report()
