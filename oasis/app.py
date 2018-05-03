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
from oasis import job
from oasis import manager as mg
from oasis import handler as hd
from oasis.libs.log import logger
from oasis.libs import alert
from oasis.manager import Manager
from oasis.handler import OasisHandler


define("config", default="", help="path to config file")
define("port", default=33338, help="service port")
define("address", default="", help="the address of external access")
define("slack_token", default="", help="slack token")
define("models_path", default="",
       help="path of models, including the config files of all models")
define("db_path", default="", help="the path of the database file")

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3

DEFAULT_DB_PATH = "./data/oasis.db"


def parse_config():
    options.parse_command_line()
    if options.config != "":
        logger.info("parse config from config file: {config}"
                    .format(config=options.config))
        options.parse_config_file(options.config)

    if options.slack_token == "":
        logger.error("slack token is required!!")
        sys.exit(1)

    if options.models_path == "":
        logger.error("models path is required!!")
        sys.exit(1)

    if options.db_path == "":
        logger.info("path of database is not set, use the default db path: {path}"
                    .format(path=DEFAULT_DB_PATH))
        options.db_path = DEFAULT_DB_PATH

    mg.MODELS_PATH = options.models_path
    alert.SLACK_TOKEN = options.slack_token
    job.REPORT_ADDRESS = options.address

    logger.info("config: {config}".format(config=options.items()))


def sig_handler(server, manager, sig, frame):
    io_loop = tornado.ioloop.IOLoop.current()

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
        manager.close()
        server.stop()
        logger.info('Will shutdown in %s seconds ...',
                    MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
        stop_loop(time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)

    logger.warning('Caught signal: %s', sig)
    io_loop.add_callback_from_signal(shutdown)


def make_app(handler):
    return tornado.web.Application([
        (r"/api/v1/job/new", handler.JobNewHandler),
        (r"/api/v1/job/(?P<job_id>[\w+|\-]+)/detail", handler.JobDetailHandler),
        (r"/api/v1/job/(?P<job_id>[\w+|\-]+)/stop", handler.JobStopHandler),
        (r"/api/v1/job/(?P<job_id>[\w+|\-]+)/report", handler.JobReportHandler),
        (r"/api/v1/jobs/list", handler.JobListHandler),
    ])


def main():
    parse_config()

    manager = Manager(options.db_path)
    hd.manager = manager

    handler = OasisHandler()

    app = make_app(handler)
    server = tornado.httpserver.HTTPServer(app)
    logger.info("oasis server start to listen {port}..."
                .format(port=options.port))
    server.listen(options.port)

    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG' + sig),
                      partial(sig_handler, server, manager))

    tornado.ioloop.IOLoop.current().start()

    logger.info("Exit...")


