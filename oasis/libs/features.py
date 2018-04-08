# -*- coding: utf-8 -*-

from __future__ import absolute_import

import numpy as np


def mean(data):
    return np.mean(data)


def std(data):
    return np.std(data)


def var(data):
    return np.std(data)


def sum(data):
    return np.sum(data)


Features = {
    "mean": mean,
    "std": std,
    "var": var,
    "sum": sum,
}

