# !/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config

import tornado.ioloop
import tornado.web
from tornado.options import options

from app.config import settings
from app.handlers import IndexHandler, RoomSocketHandler
from app.room_managers import RoomManager

def main():

    # create logger for app
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT)

    room_manager = RoomManager()

    urls = [
        (r"/$", IndexHandler),
        (r"/ws$", RoomSocketHandler, dict(room_manager=room_manager))
    ]

    application = tornado.web.Application(
        urls,
        debug=options.debug,
        autoreload=options.debug,
        **settings
    )

    # Start Server
    logger.info("Starting App on Port: {} with Debug Mode: {}".format(options.port, options.debug))

    application.listen(9000)
    tornado.ioloop.IOLoop.current().start()