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


def min(data):
    return np.min(data)


def max(data):
    return np.max(data)


def median(data):
    return np.median(data)


# return max(data) - min(data)
def ptp(data):
    return np.ptp(data)


Features = {
    "mean": mean,
    "std": std,
    "var": var,
    "sum": sum,
    "min": min,
    "max": max,
    "median": median,
    "ptp": ptp
}

