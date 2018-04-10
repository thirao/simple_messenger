#!/bin/env python
# -*- coding: utf-8 -*-
import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.log
from tornado.options import options, parse_command_line
import os
import json
import logging
import tornado.escape
import sqlite3

# debug向けの設定

dummy_article = {
    "uid": 114514,
    "author": "nameNAME",
    "published": "2016-08-10T11:45:14+09:00",
    "message": """
    AAAaaaあああ
    """
}


class Application(tornado.web.Application):
    def __init__(self):
        # ルーティングに対応するハンドラの登録
        handlers = [
            (r"/", IndexHandler),
            (r"/ws/", ChatHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/msg",MessageHandler)

        ]
        # tornadoの設定関連
        settings = dict(
            login_url="login",
            cookie_secret='k5oy9qv76V2GWFKW3A56El3v6O33hR0M',
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):

    cookie_username = "username"
    def get_current_user(self):
        username = self.get_secure_cookie(self.cookie_username)
        logging.info('BaseHandler - username: %s' % username)
        if not username: return None
        return tornado.escape.utf8(username)

    def set_current_user(self, username):
        self.set_secure_cookie(self.cookie_username, tornado.escape.utf8(username))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_username)


# トップページと記事一覧ページのハンドラ
class IndexHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        uname = self.get_current_user()
        self.render(
                "index.html",
                uname=uname
            )

class MessageHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        pass



# ログインページ
class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        logging.debug("xsrf_cookie:" + self.get_argument("_xsrf", None))
        self.check_xsrf_cookie()

        username = self.get_argument("username")
        password = self.get_argument("password")

        a = AccountDao()

        logging.info('LoginHandler:post %s %s' % (username, password))

        if a.is_account(username, password):
            self.set_current_user(username)
            self.redirect("/")
        else:
            self.write_error(403)


# ログアウトページ
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_current_user()
        self.redirect('/')


# メッセージやりとり用
class ChatHandler(tornado.websocket.WebSocketHandler):
    # ルームへ接続中のクライアント一覧
    node = set()
    nodes = dict()

    messages = []

    def initialize(self):
        pass

    def open(self):
        self.node.add(self)
        if not self.nodes.get(self.get_secure_cookie('username'), False):
            self.nodes.update({self.get_secure_cookie('username'): self})

        logging.info(self.nodes)

        # DBから会話データを取得
        self.write_message({'message':"Hello User"})
        pass

    # メッセージ到着時の処理
    def on_message(self, message):
        msg = json.loads(message)
        msg['from'] = self.get_secure_cookie('username').decode('utf-8')

        # debug時以外dbへ格納
        if not options.debug:
            logging.info(options.debug)

        logging.info(msg['date'])
        for u, h in self.nodes.items():
            logging.info(u.decode('utf-8') + ": " + msg['to'])
            if msg['to'] == u.decode('utf-8'):
                h.write_message(msg)

    # 終了時の処理
    def on_close(self):
        d = self.nodes.pop(self.get_secure_cookie('username'))
        self.node.remove(self)


class AccountDao:
    dbname = 'account.db'

    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS account(id, name, password);")
        conn.commit()
        conn.close()

    # アカウント作成
    def create_account(self, user, password):
        import uuid
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        uid = uuid.uuid4()
        print(uid)
        if self.is_account(user, password):
            return "Error"
        else:
            pass

        cur.execute("INSERT INTO account VALUES (?,?,?);", (str(uid), str(user), str(password),))
        conn.commit()
        conn.close()

    # アカウント認証
    def is_account(self, user, password):
        import uuid
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        uid = uuid.uuid4()

        cur.execute("SELECT name FROM account WHERE name=? AND password=?;", (user, password,))
        result = cur.fetchall()
        conn.close()
        if len(result) != 0:
            return True
        else:
            return False

# 全件取得
    def get_all_account(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM account;")
        result = cur.fetchall()
        conn.close()
        return result


class MessageDao:
    dbname = 'messages.db'
    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS messages(m_from, m_to, message, date);")
        conn.commit()
        conn.close()

    def get_message_by_name(self,username):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages WHERE m_to = ?;", (username,))
        result = cur.fetchall()
        conn.close()
        return result

    def set_message(self, message):
        if not message.get('from', False) and message.get('to', False) and message.get('date', False) and message.get('message', False):
            return "Error"

        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO messages VALUES (?,?,?,?);",
            (message['from'], message['to'], message['message'], str(message['date']))
        )
        conn.commit()
        conn.close()

    def get_message(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages;")
        result = cur.fetchall()
        conn.close()
        return result


def main():
    # tornadoのコマンドラインオプションの設定
    options.define('port', type=int, default='80')
    options.define('debug', type=bool, default=True)
    tornado.options.parse_command_line()
    app = Application()
    try:
        server = tornado.httpserver.HTTPServer(app)
        server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()
    finally:
        tornado.ioloop.IOLoop.current().stop()


if __name__ == "__main__":
    main()
