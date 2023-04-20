# -*- coding: utf-8 -*-
# @FileName  : app.py
# @Author： 公众号：阿三先生
# @Date 11/9/22 2:10 PM
# @Version 1.0

import tornado
import tornado.ioloop
import tornado.web
import tornado.gen
import logging

from server.server import OpenaiService
from settings import SERVICE_PORT

logging.basicConfig(level="INFO")
logger = logging.getLogger()

def make_app():
    logger.info("Project is ready ...")
    return tornado.web.Application([
        (r"/chatgpt-service/v1/chat", OpenaiService),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(SERVICE_PORT)
    tornado.ioloop.IOLoop.current().start()
    exit(0)
