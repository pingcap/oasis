# -*- coding: utf-8 -*-

import re
from oasis.libs.log import logger
from oasis.libs.iexceptions import ParseRuleException

OPERATORS = ["==", "!=", "<=", ">=", "=", "<", ">"]

FEATURE_RULE = r'^features\[(\w+)\]\s*(' \
               + '|'.join(OPERATORS) \
               + ')\s*(\d+|\.)'


def parse_rule(rules):
    rules_list = []
    for rule in rules:
        match = re.match(FEATURE_RULE, rule)
        if match:
            try:
                value = float(match.group(3))
            except Exception as e:
                logger.error("parse rule: {rule} failed, error: {err}"
                             .format(rule=rule, err=str(e)))
                raise ParseRuleException(rule=rule)

            rules_list.append({"expr": rule, "feature": match.group(1),
                               "operator": match.group(2),
                               "value": value})
        else:
            logger.error("parse rule: {rule} failed"
                         .format(rule=rule))
            raise ParseRuleException(rule=rule)

    return rules_list

