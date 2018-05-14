# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import tornado.locks
from oasis.libs.alert import DEFAULT_CHANNEL
from oasis.libs.log import logger
from oasis.job import DEFAULT_JOB_TIMEOUT
from oasis.libs.iexceptions import (
    NewJobException,
    JobNotExistsException,
    JobNotRunningException
)

HTTP_MISS_ARGS = 401
HTTP_NOT_FOUND = 404
HTTP_FAIL = 400
HTTP_OK = 200

manager = None


class OasisHandler(object):
    class JobNewHandler(tornado.web.RequestHandler):
        def post(self):
            try:
                data = json.loads(self.request.body)
            except Exception as e:
                logger.error("load json: {json_data}\nfailed: {err}"
                            .format(json_data=self.request.body, err=str(e)))
                logger.exception("Exception Logged")

                self.finish({"code": HTTP_FAIL,
                            "message": "load json data failed: {err}"
                            .format(err=str(e))})
                return

            slack_channel = data.get("slack_channel", DEFAULT_CHANNEL)
            timeout = data.get("timeout", DEFAULT_JOB_TIMEOUT)

            try:
                job = manager.new_job(data["name"], data["data_source"], data["models"],
                                      slack_channel, timeout)
            except KeyError as e:
                logger.error("add new job failed: miss args %s" % e.args[0])
                logger.exception("Exception Logged")

                data = {"code": HTTP_MISS_ARGS,
                        "message": "miss args %s" % e.args[0]}
            except NewJobException as e:
                logger.error("add new job failed: {err}"
                            .format(err=str(e)))
                logger.exception("Exception Logged")

                data = {"code": HTTP_FAIL,
                        "message": "add new job failed: {err}".format(err=str(e))}
            except Exception as e:
                logger.error("add new job failed: {err}"
                            .format(err=str(e)))
                logger.exception("Exception Logged")
                data = {"code": HTTP_FAIL,
                        "message": "add new job failed: {err}".format(err=str(e))}
            else:
                data = {"code": HTTP_OK,
                        "message": "OK", "data": job}
            finally:
                self.finish(data)

    class JobStopHandler(tornado.web.RequestHandler):
        def get(self, job_id):
            if job_id == "":
                logger.error("job id is required")
                self.finish({"code": HTTP_MISS_ARGS,
                            "message": "job id is required"})
                return

            try:
                logger.info("close running job:{job_id}"
                            .format(job_id=job_id))
                manager.stop_job(int(job_id))
            except JobNotExistsException:
                logger.error("close job:{job_id} failed: job is not exist"
                            .format(job_id=job_id))
                logger.exception("Exception Logged")

                data = {"code": HTTP_FAIL,
                        "message": "close job:{job_id} failed: job is not exist".format(job_id=job_id)}
            except JobNotRunningException:
                logger.error("close job:{job_id} failed: job is not running"
                            .format(job_id=job_id))
                logger.exception("Exception Logged")

                data = {"code": HTTP_FAIL,
                        "message": "close job:{job_id} failed: job is not running".format(job_id=job_id)}
            except Exception as e:
                logger.error("close job:{job_id} failed:{err}"
                            .format(job_id=job_id, err=str(e)))
                logger.exception("Exception Logged")

                data = {"code": HTTP_FAIL,
                        "message": "close job:{job_id} failed:{err}".format(job_id=job_id, err=str(e))}
            else:
                data = {"code": HTTP_OK, "message": "OK"}
            finally:
                self.finish(data)

    class JobListHandler(tornado.web.RequestHandler):
        def get(self):
            logger.info("list all jobs")
            jobs = manager.list_all_job()
            self.finish({"code": HTTP_OK, "message": "OK", "data": jobs})

    class JobDetailHandler(tornado.web.RequestHandler):
        def get(self, job_id):
            if job_id == "":
                logger.error("job id is required")
                self.finish({"code": HTTP_MISS_ARGS,
                            "message": "job id is required"})
                return

            try:
                logger.info("get job:{job_id} detail"
                            .format(job_id=job_id))
                job = manager.get_job(int(job_id))
            except JobNotExistsException:
                logger.error("get job:{job_id} detail failed: job is not exist"
                            .format(job_id=job_id))
                logger.exception("Exception Logged")

                data = {"code": HTTP_NOT_FOUND,
                        "message": "get job:{job_id} failed: job is not exist".format(job_id=job_id)}
            except Exception as e:
                logger.error("get job:{job_id} detail failed:{err}"
                            .format(job_id=job_id, err=str(e)))
                logger.exception("Exception Logged")

                data = {"code": HTTP_FAIL,
                        "message": "get job:{job_id} detail failed:{err}"
                            .format(job_id=job_id, err=str(e))}
            else:
                data = {"code": HTTP_OK, "message": "OK", "data": job}
            finally:
                self.finish(data)

    class ModelTemplatesListHandler(tornado.web.RequestHandler):
        def get(self):
            logger.info("list all model templates")
            templates = manager.list_all_model_templates()

            self.finish({"code": HTTP_OK, "message": "OK", "data": templates})

    class MetricsListHandler(tornado.web.RequestHandler):
        def get(self):
            logger.info("list all metrics")

            metrics = manager.list_all_metrics()

            self.finish({"code": HTTP_OK, "message": "OK", "data": metrics})


