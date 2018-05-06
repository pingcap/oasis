#!/usr/bin/env bash

json_data='''
{
    "data_source": {
        "url": "http://40.125.162.12:34470"
    },
    "timeout": "24h",
    "models": [
        {
            "name": "iForest",
            "metrics": ["qps"],
            "config": {
                "model": {
                    "train_count": 120,
                    "train_interval": "60s",
                    "predict_interval": "300s"
                }
            }
        },
        {
            "name": "rules",
            "metrics": ["qps"],
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
    ]
}
'''


curl -H "Content-Type: application/json" \
    -X POST \
    -d "${json_data}" \
http://127.0.0.1:33338/api/v1/job/new
