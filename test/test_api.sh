#!/usr/bin/env bash

json_data='''
{
    "data_source": {
        "url": "http://40.125.162.12:38175"
    },
    "model": "iForest",
    "metrics": ["qps", "latency"],
    "timeout": "24h"
}
'''

curl -H "Content-Type: application/json" \
    -X POST \
    -d "${json_data}" \
http://127.0.0.1:2333/api/v1/job/new
