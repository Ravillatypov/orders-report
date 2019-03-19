from datetime import datetime, time, timedelta
import pymysql


class Report:
    _start_time = time(9, 0)
    _stop_time = time(19, 0)
    expired = 0
    done = 0
    created = 0

    def __init__(self, settings: dict):
        self._database_url = settings.get('db', {})
        now = datetime.now()
        self.current_time = now.time()
        self.today = now.date()
        if self.today.weekday() in (5, 6):
            self._stop_time = time(16, 0)

    def get_report(self):
        pass

    def get_orders_list(self, created_from, created_to):
        pass
        
    def _get_counts_from_db(self):
        pass

    def at_start_time(self):
        pass

    def at_morning(self):
        pass

    def at_daytime(self):
        pass

    def at_stop_time(self):
        pass
