# -*- coding: utf-8 -*-

from __future__ import absolute_import

import uuid
import json
import tornado.gen
import tornado.web
import tornado.locks
from concurrent.futures import ThreadPoolExecutor
from oasis.libs.alert import DEFAULT_CHANNEL
from oasis.libs.log import logger
from oasis.job import Job

HTTP_MISS_ARGS = 401
HTTP_ARGS_NOT_VALID = 402
HTTP_FAIL = 403
HTTP_OK = 200

runners = dict()
lock = tornado.locks.Lock()


class ModelHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=24)

    @tornado.gen.coroutine
    def run(self, job):
        try:
            if not job.valid():
                raise ValueError("job {job} is invalid"
                                 .format(job=job.to_dict()))
        except Exception:
            raise ValueError("job {job} is invalid"
                             .format(job=job.to_dict()))

        result = yield self._async_execute(job)
        raise tornado.gen.Return(result)

    @tornado.concurrent.run_on_executor
    def _async_execute(self, job):
        job.run()
        lock.acquire()
        runners[job.id] = job
        lock.release()
        return True

    @staticmethod
    def close_job(job_id):
        if job_id not in runners:
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))

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
            job = runner.job.to_dict()
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

        return runner.job.to_dict()


class JobNewHandler(ModelHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
        except Exception as e:
            logger.error("load json: {json_data}\nfailed: {err}"
                         .format(json_data=self.request.body, err=str(e)))
            self.finish({"code": HTTP_FAIL,
                         "message": "load json data failed: {err}"
                        .format(err=str(e))})
            return

        slack_channel = data.get("slack_channel", DEFAULT_CHANNEL)

        try:
            job = Job(str(uuid.uuid4()), data["data_source"],
                      data["models"], slack_channel)
        except KeyError as e:
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "miss args %s" % e.args[0]})
            return

        try:
            logger.info("run new job:{job}"
                        .format(job=job.to_dict()))
            self.run(job)
        except Exception as e:
            logger.error("run job:{job} failed:{err}"
                         .format(job=job.to_dict(), err=str(e)))
            self.finish({"code": HTTP_FAIL,
                         "message": "run job:{job} failed:{err}"
                        .format(job=job.to_dict(), err=str(e))})

        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": job.to_dict()})


class JobDeleteHandler(ModelHandler):
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
    def get(self):
        logger.info("list all running jobs")
        jobs = self.list_jobs()
        logger.info("running jobs:{jobs}"
                    .format(jobs=jobs))
        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": jobs})


class JobDetailHandler(ModelHandler):
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






