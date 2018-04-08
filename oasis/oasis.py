# -*- coding: utf-8 -*-

from __future__ import absolute_import

import uuid
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import tornado.gen
import tornado.web
from oasis.models import models
from oasis.libs.alert import send_to_slack, DEFAULT_CHANNEL
from oasis.libs.log import logger
from oasis.job import Job, DEFAULT_JOB_TIMEOUT

HTTP_MISS_ARGS = 401
HTTP_FAIL = 403
HTTP_OK = 200

runners = dict()
lock = threading.Lock()


class ModelHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=24)

    @tornado.gen.coroutine
    def run(self, job):
        if job.model not in models:
            raise ValueError("model:{model} is not supported"
                             .format(model=job.model))
            # raise ModelNotSupportException(model_name=job.model)

        model = models[job.model]
        runner = model(job, send_to_slack)
        lock.acquire()
        runners[job.id] = runner
        lock.release()

        result = yield self._async_execute(runner)
        raise tornado.gen.Return(result)

    @tornado.concurrent.run_on_executor
    def _async_execute(self, runner):
        runner.run()
        return True

    @staticmethod
    def close_job(job_id):
        if job_id not in runners:
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
            # raise JobNotExistsException(job_id=job_id)
        lock.acquire()
        runner = runners[job_id]
        runner.close()

        del runners[job_id]
        lock.release()

    @staticmethod
    def list_jobs():
        lock.acquire()
        jobs = []
        for job_id, runner in runners.items():
            job = dict(runner.job)
            jobs.append(job)
        lock.release()
        return jobs

    @staticmethod
    def close_all_jobs():
        lock.acquire()
        for runner in runners.values():
            runner.close()
        lock.release()

    @staticmethod
    def detail_job(job_id):
        if job_id not in runners:
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
            # raise JobNotExistsException(job_id=job_id)
        lock.acquire()
        runner = runners[job_id]
        lock.release()

        return dict(runner.job)


class JobNewHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body)
        print(data)
        try:
            slack_channel = data.get("slack_channel", DEFAULT_CHANNEL)

            timeout = data.get("timeout", DEFAULT_JOB_TIMEOUT)

            config = data.get("config", None)

            job = Job(str(uuid.uuid4()), data["data_source"],
                      data["model"], data["metrics"],
                      slack_channel, timeout, config)
        except KeyError as e:
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "miss args %s" % e.args[0]})

        try:
            logger.info("run new job:{job}"
                        .format(job=dict(job)))
            self.run(job)
            self.finish({"code": HTTP_OK,
                        "message": "OK",
                         "data": dict(job)})
        except Exception as e:
            logger.error("run job:{job} failed:{err}"
                         .format(job=dict(job), err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "run job:{job} failed:{err}"
                        .format(job=dict(job), err=e)})


class JobDeleteHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})

        try:
            logger.info("close running job:{job_id}"
                        .format(job_id=job_id))
            self.close_job(job_id)
            self.finish({"code": HTTP_OK,
                        "message": "OK"})
        except Exception as e:
            logger.error("close job:{job_id} failed:{err}"
                         .format(job_id=job_id, err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "close job:{job_id} failed:{err}"
                        .format(job_id=job_id, err=e)})


class JobListHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        logger.info("list all running jobs")
        jobs = self.list_jobs()
        logger.info("running jobs:{jobs}"
                    .format(jobs=jobs))
        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": jobs})


class JobDetailHandler(ModelHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})

        try:
            logger.info("get job:{job_id} detail"
                        .format(job_id=job_id))
            job = self.detail_job(job_id)
            self.finish({"code": HTTP_OK,
                         "message": "OK",
                         "data": job})
        except Exception as e:
            logger.error("get job:{job_id} detail failed:{err}"
                         .format(job_id=job_id, err=e))
            self.finish({"code": HTTP_FAIL,
                         "message": "get job:{job_id} detail failed:{err}"
                        .format(job_id=job_id, err=e)})






