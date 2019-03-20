from report import Report
from tg import TelegramAPI, print_message, send

if __name__ == '__main__':
    r = Report({'host': '127.0.0.1',
                'user': 'appuser',
                'password': 'app_password',
                'db': 'app_db',
                'charset': 'utf8'})
    message = r.get_report()
    if r.expired > 0 and len(message):
        args = ['tg', 'Telegram group', message, '', '--group']
        send(args)
