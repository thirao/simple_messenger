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
from database import AccountDao, MessageDao
import settings as s


class Application(tornado.web.Application):
    def __init__(self):
        # ルーティングに対応するハンドラの登録
        handlers = [
            (r"/", IndexHandler),
            (r"/ws/", ChatHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/user", GetUserHandler),
            (r"/signup", CreateAccountHandler),
        ]
        # tornadoの設定関連
        settings = dict(
            login_url="login",
            cookie_secret=s.COOKIE_SECRET,
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
        # logging.info('BaseHandler - username: %s' % username)
        if not username: return None
        return tornado.escape.utf8(username)

    def set_current_user(self, username):
        self.set_secure_cookie(self.cookie_username, tornado.escape.utf8(username))

    def clear_current_user(self):
        self.clear_cookie(self.cookie_username)


# トップページ
class IndexHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        uname = self.get_current_user()
        self.render(
                "index.html",
                uname=uname
            )


class GetUserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(self.current_user.decode('utf-8'))


class CreateAccountHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        a = AccountDao()
        self.check_xsrf_cookie()

        username = self.get_argument("username")
        password = self.get_argument("password")

        a = AccountDao()

        if a.is_exist_user(username,):
            logging.info("Account Exist: %s" % (username,))
            self.send_error(403)

        else:
            a.create_account(username, password)
            logging.info("New Account: %s" % (username,))
            self.redirect("/")


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
        logging.info("Logout User: %s", self.get_current_user())
        self.clear_current_user()
        self.redirect('/')


# メッセージやりとり用
class ChatHandler(tornado.websocket.WebSocketHandler):
    # ルームへ接続中のクライアント一覧
    node = set()
    # key: user-name, value: connection
    nodes = dict()

    messages = []
    def initialize(self):
        pass

    # 接続時の処理
    def open(self):
        self.node.add(self)
        # 接続ノード一覧へ追加
        if not self.nodes.get(self.get_secure_cookie('username'), False):
            self.nodes.update({self.get_secure_cookie('username'): self})

        # logging.info(self.nodes)

        # DBから会話データを取得
        b = MessageDao()
        messages = b.get_message_by_name(self.get_secure_cookie('username').decode('utf-8'))

        self.write_message(json.dumps(messages))

    # メッセージ到着時の処理
    def on_message(self, message):
        msg = json.loads(message)
        msg['from'] = self.get_secure_cookie('username').decode('utf-8')

        # debug時以外dbへ格納
        if not options.debug:
            b = MessageDao()
            b.set_message(msg)
            logging.info(options.debug)

        # 接続中のユーザーへ送信
        for u, h in self.nodes.items():
            logging.info(u.decode('utf-8') + ": send message to: " + msg.get('to', "Empty User"))
            if (msg.get('to', False) == u.decode('utf-8')) or (msg.get('from', False) == u.decode('utf-8')):
                h.write_message(json.dumps([msg]))

    # 終了時の処理
    def on_close(self):
        if self.nodes.get(self.get_secure_cookie('username'),False):
            d = self.nodes.pop(self.get_secure_cookie('username'))
        if self in self.node:
            self.node.remove(self)


def main():
    # tornadoのコマンドラインオプションの設定
    options.define('port', type=int, default='8000')
    options.define('debug', type=bool, default=False)
    tornado.options.parse_command_line()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
