# -*- coding:utf-8 -*-

import os

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello world')


class CaptchaHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('captcha.html', **{
            'title': u'验证码',
            'msg': u'欢迎使用Simple-Captcha'
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
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    application = Application()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
