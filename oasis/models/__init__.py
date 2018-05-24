# -*- coding: utf-8 -*-

from __future__ import absolute_import

from oasis.models.model import Model
from oasis.models.iforest import IForest, IFOREST_MODEL_NAME
from oasis.models.rules import Rules, RULES_MODEL_NAME

Models = {
    IFOREST_MODEL_NAME: IForest,
    RULES_MODEL_NAME: Rules,
}
