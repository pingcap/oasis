# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from slackclient import SlackClient
from oasis.libs.log import logger


DEFAULT_CHANNEL = "#schordinger-alert"
SLACK_TOKEN = ""


def send_to_slack(message, channel=DEFAULT_CHANNEL):
    sc = SlackClient(SLACK_TOKEN)

    try:
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
            username="metrics_bot",
            timeout="3s",
        )
    except Exception as e:
        logger.error("send message:{message} to slack channel:{channel} failed, error:{error}"
                     .format(message=message, channel=channel, error=e))



