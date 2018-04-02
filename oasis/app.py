# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import time
from functools import partial
from tornado.options import define, options
import tornado.web
import tornado.httpserver
import tornado.ioloop
import signal
from oasis.libs.log import logger
from oasis.libs import alert
from oasis.oasis import (
    JobNewHandler,
    JobDeleteHandler,
    JobListHandler,
    JobDetailHandler,
    ModelHandler
)


define("config", default="../docs/app.conf", help="path to config file")
define("port", default=2333, help="service port")
define("slack_token", default="", help="slack token")

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3


def parse_config():
    options.parse_command_line()
    if options.config != "":
        logger.info("parse config from config file: {config}"
                    .format(config=options.config))
        options.parse_config_file(options.config)

    if options.slack_token == "":
        logger.error("slack token is required!!")
        sys.exit(1)

    alert.SLACK_TOKEN = options.slack_token
    logger.info("config: {config}".format(config=options.items()))


def sig_handler(server, sig, frame):
    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(deadline):
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            logger.info('Waiting for next tick')
            io_loop.add_timeout(now + 1, stop_loop, deadline)
        else:
            io_loop.stop()
            logger.info('Shutdown finally')

    def shutdown():
        logger.info('Stopping http server')
        server.stop()
        ModelHandler.close_all_jobs()
        logger.info('Will shutdown in %s seconds ...',
                    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        stop_loop(time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    logger.warning('Caught signal: %s', sig)
    io_loop.add_callback_from_signal(shutdown)


def make_app():
    return tornado.web.Application([
        (r"/api/v1/job/new", JobNewHandler),
        (r"/api/v1/job/(?P<job_id>[\w+|\-]+)/detail", JobDetailHandler),
        (r"/api/v1/job/(?P<job_id>[\w+|\-]+)/delete", JobDeleteHandler),
        (r"/api/v1/jobs/list", JobListHandler),
    ])


def main():
    parse_config()

    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    logger.info("oasis server start to listen {port}..."
                .format(port=options.port))
    server.listen(options.port)

    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG' + sig),
                      partial(sig_handler, server))

    tornado.ioloop.IOLoop.current().start()

    logger.info("Exit...")


