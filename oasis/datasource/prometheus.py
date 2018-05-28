# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import requests
import csv
from oasis.datasource.data_model import DataModel

# Create a metric to track time spent and requests made.
# REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
QUERY_API = "/api/v1/query"
RANGE_QUERY_API = "/api/v1/query_range"
Metrics = {
    "qps":
    "sum(rate(tidb_server_query_total[1m])) by (status)",
    "80_latency":
    "histogram_quantile(0.80, sum(rate(tidb_server_handle_query_duration_seconds_bucket[1m])) by (le))",
    "95_latency":
    "histogram_quantile(0.95, sum(rate(tidb_server_handle_query_duration_seconds_bucket[1m])) by (le))",
    "99_latency":
    "histogram_quantile(0.99, sum(rate(tidb_server_handle_query_duration_seconds_bucket[1m])) by (le))",
    "connection_count":
    "sum(tidb_server_connections)",
    "ticlient_region_error":
    "sum(rate(tidb_tikvclient_region_err_total[1m]))",
    "pd_request_duration":
    "sum(rate(tikv_pd_request_duration_seconds_sum[1m])) / sum(rate(tikv_pd_request_duration_seconds_count[1m]))",
    "lock_resolve_qps":
    "sum(rate(tidb_tikvclient_lock_resolver_actions_total[1m]))",
    "95_ddl_second":
    "histogram_quantile(0.95, sum(rate(tidb_ddl_handle_job_duration_seconds_bucket[1m])) by (le))",
    "server_is_busy":
    "sum(rate(tikv_scheduler_too_busy_total[1m]))",
    "channel_full":
    "sum(rate(tikv_channel_full_total[1m]))",
    "raftstore_error":
    "sum(rate(tikv_storage_engine_async_request_total{status!~'success|all'}[1m]))",
    "coprocessor_error":
    "sum(rate(tikv_grpc_msg_fail_total[1m]))",
    "PD_cluster_lost_connect_tikv_nums":
    "sum(pd_cluster_status{type='store_disconnected_count'})",
    "PD_leader_change":
    "count(changes(pd_server_tso{type='save'}[10m]) > 0)",
    "PD_miss_peer_region_count":
    "sum( pd_regions_status{type='miss_peer_region_count'} )",
    "PD_server_is_down":
    "probe_success{group='pd'}",
    "TiDB_ddl_waiting_jobs":
    "sum(tidb_ddl_waiting_jobs)",
    "TiDB_schema_error":
    "increase(tidb_session_schema_lease_error_total{type='outdated'}[15m])",
    "TiDB_server_event_error":
    "increase(tidb_server_server_event{type=~'server_start|server_hang'}[15m])",
    "TiKV_write_stall":
    "delta( tikv_engine_write_stall[10m])"
}


class PrometheusAPI(DataModel):
    """Prometheus api client"""

    def __init__(self, data_source):
        self._query_api = QUERY_API
        self._range_query_api = RANGE_QUERY_API
        self.data_source = data_source

    def query(self, query):
        data_set = dict()
        try:
            response = requests.get(
                self.data_source.url + self._range_query_api,
                params={
                    'query': query.expr,
                    'start': query.start_time,
                    'end': query.end_time,
                    'step': query.step
                })
            status = response.json()['status']

            if status == "error":
                logging.error(response.json())
                return

            results = response.json()['data']['result']
            if len(results):
                for value in results[0]['values']:
                    data_set[value[0]] = value[1]
        except Exception as e:
            logging.error(
                "datasource: {datasource}, query: {query}, failed: {err}".
                format(
                    datasource=self.data_source.to_dict(),
                    query=query.to_dict,
                    err=str(e)))
            logging.exception("Exception Logged")
        finally:
            return data_set


class PrometheusQuery(object):
    def __init__(self, expr, start_time, end_time, step):
        self.expr = expr
        self.start_time = start_time
        self.end_time = end_time
        self.step = step

    def to_dict(self):
        return {
            "expr": self.expr,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "step": self.step
        }


def write2csv(filename, model, ids, data_set):
    with open(filename, model) as f:
        writer = csv.writer(f)
        # for timestamp in sorted(data_set.keys(), reverse=True):
        #    writer.writerow([timestamp] + data_set[timestamp])
        # writer.writeheader()
        for data in data_set.values():
            writer.writerow([ids, data])
