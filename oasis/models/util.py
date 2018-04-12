# -*- coding: utf-8 -*-
from __future__ import absolute_import

import collections

JOB_ID_LEN = 8
EPS = 0.00001


def sub_id(st):
    if len(st) < JOB_ID_LEN:
        return st

    return st[0:JOB_ID_LEN]


class Struct(object):
    def __init__(self, dict_data):
        """Convert a dictionary to a class

        @param :dict_data Dictionary
        """
        self.__dict__.update(dict_data)
        for k, v in dict_data.items():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)
            if isinstance(v, collections.Iterable):
                    self.__dict__[k] = [Struct(i) if isinstance(i, dict) else i for i in v]


def get_object(dict_data):
    """Convert a dictionary to a class

    @param :dict_data Dictionary
    @return :class:Struct
    """
    return Struct(dict_data)

