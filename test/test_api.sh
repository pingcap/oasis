#!/usr/bin/env bash

json_data='''
{
    "data_source": {
        "url": "http://40.125.162.12:31802"
    },
    "model": "iForest",
    "metrics": ["qps"],
    "timeout": "24h",
    "config": {
        "model": {
            "train_count": 120,
            "train_interval": 60,
            "predict_interval": 300
        }
    }
}
'''

curl -H "Content-Type: application/json" \
    -X POST \
    -d "${json_data}" \
http://127.0.0.1:2333/api/v1/job/new
