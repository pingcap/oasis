#!/usr/bin/env bash

json_iforest='''
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
            "train_interval": "60s",
            "predict_interval": "300s"
        }
    }
}
'''

json_rules='''
{
    "data_source": {
        "url": "http://40.125.162.12:31802"
    },
    "model": "rules",
    "metrics": ["qps"],
    "timeout": "24h",
    "config": {
        "model": {
            "data_range": "10m",
            "predict_interval": "2m"
        },
        "metrics": {
            "qps": {
                "features": ["mean", "std"],
                "rules": [
                    "features[std] > 300"
                ]
            }
        }
    }
}
'''

curl -H "Content-Type: application/json" \
    -X POST \
    -d "${json_rules}" \
http://127.0.0.1:2333/api/v1/job/new
