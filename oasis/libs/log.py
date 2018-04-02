# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging
import sys
from tornado.log import gen_log, access_log, app_log


formatter = logging.Formatter(
    fmt='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
    datefmt='%y/%m/%d %H:%M:%S')


def get_logger():
    """
    @summary: init logger
    @result: return a logger object
    """
    logger_ = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    logger_.setLevel(logging.INFO)
    return logger_


def set_tornado_log():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    gen_log.addHandler(handler)
    gen_log.setLevel(logging.INFO)

    access_log.addHandler(handler)
    access_log.setLevel(logging.INFO)

    app_log.addHandler(handler)
    access_log.setLevel(logging.INFO)


set_tornado_log()
logger = get_logger()

