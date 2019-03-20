import sys
import os
import time
import random
import requests
import json
import stat
import tgsettings as cfg


class TelegramAPI():
    tg_url_bot_general = "https://api.telegram.org/bot"

    def http_get(self, url):
        res = requests.get(url, proxies=self.proxies)
        answer = res.text
        if sys.version[0] == '3':
            answer_json = json.loads(answer)
        else:
            answer_json = json.loads(answer.decode('utf8'))
        return answer_json

    def __init__(self, key):
        self.debug = False
        self.key = key
        self.proxies = {}
        self.type = "private"  # 'private' for private chats or 'group' for group chats
        self.markdown = False
        self.html = False
        self.disable_web_page_preview = False
        self.disable_notification = False
        self.reply_to_message_id = 0
        self.tmp_uids = None

    def setting(self, debug=False, proxy={}, msgtype='private', markdown=False, 
    html=False, disable_web_page_preview=False, disable_notification=False, tmp_uids=None):
        self.debug = debug
        self.proxies = proxy
        self.type = msgtype
        self.markdown = markdown
        self.html= html
        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview
        self.tmp_uids = tmp_uids

    def get_me(self):
        url = self.tg_url_bot_general + self.key + "/getMe"
        me = self.http_get(url)
        return me

    def get_updates(self):
        url = self.tg_url_bot_general + self.key + "/getUpdates"
        if self.debug:
            print_message(url)
        updates = self.http_get(url)
        if self.debug:
            print_message("Content of /getUpdates:")
            print_message(updates)
        if not updates["ok"]:
            print_message(updates)
            return updates
        else:
            return updates

    def send_message(self, to, message):
        url = self.tg_url_bot_general + self.key + "/sendMessage"
        message = "\n".join(message)
        params = {"chat_id": to, "text": message, "disable_web_page_preview": self.disable_web_page_preview,
                  "disable_notification": self.disable_notification}
        if self.reply_to_message_id:
            params["reply_to_message_id"] = self.reply_to_message_id
        if self.markdown or self.html:
            parse_mode = "HTML"
            if self.markdown:
                parse_mode = "Markdown"
            params["parse_mode"] = parse_mode
        if self.debug:
            print_message("Trying to /sendMessage:")
            print_message(url)
            print_message("post params: " + str(params))
        res = requests.post(url, params=params, proxies=self.proxies)
        answer = res.text
        #answer_json = json.loads(answer)
        if sys.version[0] == '3':
            answer_json = json.loads(answer)
        else:
            answer_json = json.loads(answer.decode('utf8'))
        if not answer_json["ok"]:
            print_message(answer_json)
            return answer_json
        else:
            return answer_json

    def send_photo(self, to, message, path):
        url = self.tg_url_bot_general + self.key + "/sendPhoto"
        message = "\n".join(message)
        params = {"chat_id": to, "caption": message, "disable_notification": self.disable_notification}
        if self.reply_to_message_id:
            params["reply_to_message_id"] = self.reply_to_message_id
        files = {"photo": open(path, 'rb')}
        if self.debug:
            print_message("Trying to /sendPhoto:")
            print_message(url)
            print_message(params)
            print_message("files: " + str(files))
        res = requests.post(url, params=params, files=files, proxies=self.proxies)
        answer = res.text
        #answer_json = json.loads(answer)
        if sys.version[0] == '3':
            answer_json = json.loads(answer)
        else:
            answer_json = json.loads(answer.decode('utf8'))
        if not answer_json["ok"]:
            print_message(answer_json)
            return answer_json
        else:
            return answer_json

    def get_uid(self, name):
        uid = 0
        if self.debug:
            print_message("Getting uid from /getUpdates...")
        updates = self.get_updates()
        for m in updates["result"]:
            if "message" in m:
                chat = m["message"]["chat"]
            elif "edited_message" in m:
                chat = m["edited_message"]["chat"]
            if chat["type"] == self.type == "private":
                if "username" in chat:
                    if chat["username"] == name:
                        uid = chat["id"]
            if (chat["type"] == "group" or chat["type"] == "supergroup") and self.type == "group":
                if "title" in chat:
                    if chat["title"] == name:
                        uid = chat["id"]
        return uid

    def error_need_to_contact(self, to):
        if self.type == "private":
            print_message("User '{0}' needs to send some text bot in private".format(to))
        if self.type == "group":
            print_message("You need to mention your bot in '{0}' group chat (i.e. type @YourBot)".format(to))

    def update_cache_uid(self, name, uid, message="Add new string to cache file"):
        cache_string = "{0};{1};{2}\n".format(name, self.type, str(uid).rstrip())
        # FIXME
        if self.debug:
            print_message("{0}: {1}".format(message, cache_string))
        with open(self.tmp_uids, "a") as cache_file_uids:
            cache_file_uids.write(cache_string)

    def get_uid_from_cache(self, name):
        uid = 0
        if os.path.isfile(self.tmp_uids):
            with open(self.tmp_uids, 'r') as cache_file_uids:
                cache_uids_old = cache_file_uids.readlines()

            for u in cache_uids_old:
                u_splitted = u.split(";")
                if name == u_splitted[0] and self.type == u_splitted[1]:
                    uid = u_splitted[2]

        return uid


def print_message(string):
    string = str(string) + "\n"
    filename = sys.argv[0].split("/")[-1]
    sys.stderr.write(filename + ": " + string)

def send(args):
    tmp_need_update = False  # do we need to update cache file with uids or not

    tmp_dir = cfg.tmp_dir
    log_file = cfg.log_file
    tg_chat = False
    tg_group = False
    is_debug = False
    rnd = random.randint(0, 999)
    ts = time.time()
    hash_ts = str(ts) + "." + str(rnd)

    to = args[1]
    subject = args[2]
    body = args[3]

    tg = TelegramAPI(key=cfg.tg_key)

    tg.tmp_uids = cfg.tmp_uids
    tg_body = (subject + "\n" + body).splitlines()
    tg_body_text = []
    for line in tg_body:
            tg_body_text.append(line)
    if "--group" in args:
        tg_chat = True
        tg_group = True
        tg.type = "group"

    if "--debug" in args or cfg.debug:
        is_debug = True
        tg.debug = True
        print_message(tg.get_me())
        print_message("Cache file with uids: " + tg.tmp_uids)
        log_file = cfg.tmp_dir + ".debug." + hash_ts + ".log"

    if "--markdown" in args or cfg.markdown:
        tg.markdown = True

    if "--html" in args or cfg.html:
        tg.html = True

    if "--channel" in args:
        tg.type = "channel"

    if "--disable_web_page_preview" in args:
        if is_debug:
            print_message("'disable_web_page_preview' option has been enabled")
        tg.disable_web_page_preview = True

    if not os.path.isdir(tmp_dir):
        if is_debug:
            print_message("Tmp dir doesn't exist, creating new one...")
        try:
            os.makedirs(tmp_dir)
            open(tg.tmp_uids, "a").close()
            os.chmod(tmp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            os.chmod(tg.tmp_uids, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        except:
            tmp_dir = "/tmp"
        if is_debug:
            print_message("Using {0} as a temporary dir".format(tmp_dir))

    uid = None

    if tg.type == "channel":
        uid = to
    else:
        to = to.replace("@", "")

    if not uid:
        uid = tg.get_uid_from_cache(to)

    if not uid:
        uid = tg.get_uid(to)
        if uid:
            tmp_need_update = True
    if not uid:
        tg.error_need_to_contact(to)
        sys.exit(1)

    if tmp_need_update:
        tg.update_cache_uid(to, str(uid).rstrip())

    if is_debug:
        print_message("Telegram uid of {0} '{1}': {2}".format(tg.type, to, uid))

    result = tg.send_message(uid, tg_body_text)
    if not result["ok"]:
        if result["description"].find("migrated") > -1 and result["description"].find("supergroup") > -1:

            migrate_to_chat_id = result["parameters"]["migrate_to_chat_id"]
            tg.update_cache_uid(to, migrate_to_chat_id, message="Group chat is migrated to supergroup, updating cache file")
            uid = migrate_to_chat_id
            result = tg.send_message(uid, tg_body_text)


if __name__ == "__main__":
    send(sys.argv)
