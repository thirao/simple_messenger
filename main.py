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


# debug向けの設定
page_len = 10

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
            (r"/ws/", ChatHandler)
        ]
        # tornadoの設定関連
        settings = dict(
            cookie_secret='k5oy9qv76V2GWFKW3A56El3v6O33hR0M',
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


# トップページと記事一覧ページのハンドラ
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render(
                "index.html"
            )


# websocket動作デモ用
class ChatHandler(tornado.websocket.WebSocketHandler):
    # ルーム一覧
    __roomList = {}
    # ルームへ接続中のクライアント一覧
    node = set()

    def initialize(self):
        pass

    def open(self):
        self.node.add(self)
        pass

    # メッセージ到着時の処理
    def on_message(self, message):
        msg = json.loads(message)
        for w in self.node:
            w.write_message(msg)

    # 終了時の処理
    def on_close(self):
        self.node.remove(self)


def main():
    # tornadoのコマンドラインオプションの設定
    options.define('port', type=int, default='80')
    options.define('debug', type=bool, default=False)

    tornado.options.parse_command_line()
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
