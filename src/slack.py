#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Repository: https://github.com/h-otter/zabbix-slackpy

from json import loads
from json import dumps
from sys import argv


def send_trigger(message, slack_hook):
    """
    On zabbix, set actions to architect message like this
    {
        "date": "{DATE} / {TIME}",
        "host": "{HOST.NAME}",
        "name": "{TRIGGER.NAME}",
        "url": "{TRIGGER.URL}",
        "status": "{TRIGGER.STATUS}",
        "triage": "{TRIGGER.SEVERITY}",
        "item_name": "{ITEM.NAME}",
        "item_value": "{ITEM.VALUE}"
    }
    """
    title = "%s: %s" % (message["status"], message["name"])

    if message["status"] == "PROBLEM":
        if message["triage"] == "Disaster":
            color = "#e45959"
        elif message["triage"] == "High":
            color = "#e97659"
        elif message["triage"] == "Average":
            color = "#ffa059"
        elif message["triage"] == "Warning":
            color = "#ffc859"
        elif message["triage"] == "Information":
            color = "#7499ff"
        else:
            color = "#97aab3"
    elif message["status"] == 'OK':
        if message["triage"] in {"Disaster", "High", "Average", "Warning"}:
            color = "good"
        else:
            return
    else:
        raise Exception("Input other status")

    payload = {
        "attachments": [
            {
                "fallback": "%s - %s." % (message["date"], title),
                "color": color,
                "author_name": message["triage"],
                "title": title,
                "title_link": message["url"],
                "fields": [
                    {
                        "title": "Data",
                        "value": message["date"],
                        "short": True
                    },
                    {
                        "title": "Host",
                        "value": message["host"],
                        "short": True
                    },
                    {
                        "title": "Detail",
                        "value": "%s: %s" % (message["item_name"], message["item_value"]),
                        "short": True
                    },
                ],
            }
        ]
    }

    value = dumps(payload).encode("utf-8")
    headers = {'Content-type':'application/json'}

    try:
        import urllib2 as urllib_req
    except ImportError:
        import urllib.request as urllib_req

    req = urllib_req.Request(slack_hook,
                             data=value,
                             headers=headers)
    return urllib_req.urlopen(req).read()


if __name__ == "__main__":
    """
    On zabbix, set media type for slack like these
    - parameters
        - {ALERT.SENDTO} -> set Slack hook URL on user configuration
        - {ALERT.MESSAGE}
    """
    argvs = argv
    if len(argvs) < 3:
        print("\nToo few arguments -- requires: (slack_hook message). Example console run:\n")
        print("""python slack.py https://hooks.slack.com/services/SLACKHOSTID '{ "date": "2020-01-01 / 00:00:01", "host": "times.square", "name": "NewYears", "url": "https://www.timeanddate.com/countdown/newyear", "status": "PROBLEM", "triage": "Warning", "item_name": "Countdown Clock", "item_value": "Almost there" }' """ + "\n")
    else:
        loaded = loads(argvs[2])
        send_trigger(loaded, argvs[1])
