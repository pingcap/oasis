# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

JOB_ID_LEN = 8


def sub_id(st):
    if len(st) < JOB_ID_LEN:
        return st

    return st[0:JOB_ID_LEN]
