# -*- coding:utf-8 -*-

import os
import time

import tornado.ioloop
import tornado.web
import ujson

import session

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = session.Session(self.application.session_manager, self)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello world')


class CaptchaHandler(BaseHandler):
    def get(self):
        self.session['test'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.session.save()
        self.render('captcha.html', **{
            'title': u'验证码',
            'msg': u'欢迎使用Simple-Captcha',
            'data': ujson.dumps(self.session)
        })


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/captcha', CaptchaHandler),
        ]

        settings = dict(
            #模板路径
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            #静态文件路径
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret = "e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
            session_secret = "3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
            session_timeout = 60,
            store_options = {
                'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_pass': '',
            },
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_manager = session.SessionManager(settings["session_secret"]
        , settings["store_options"], settings["session_timeout"])


if __name__ == '__main__':
    application = Application()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
