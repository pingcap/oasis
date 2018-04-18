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
from oasis.job import Job, DEFAULT_JOB_TIMEOUT

HTTP_MISS_ARGS = 401
HTTP_ARGS_NOT_VALID = 402
HTTP_FAIL = 403
HTTP_OK = 200

runners = dict()
lock = tornado.locks.Lock()


class JobHandler(tornado.web.RequestHandler):
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
        lock.acquire()
        if job_id not in runners:
            lock.release()
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
        job = runners[job_id]
        job.close()

        del runners[job_id]
        lock.release()

    @staticmethod
    def list_jobs():
        lock.acquire()
        jobs = []
        for job_id, job in runners.items():
            jobs.append(job.to_dict())
        lock.release()
        return jobs

    @staticmethod
    def close_all_jobs():
        lock.acquire()
        for job in runners.values():
            job.close()
        lock.release()

    @staticmethod
    def job_detail(job_id):
        lock.acquire()
        if job_id not in runners:
            lock.release()
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))
        job = runners[job_id]
        lock.release()

        return job.to_dict()

    @staticmethod
    def job_report(job_id):
        lock.acquire()
        if job_id not in runners:
            lock.release()
            raise ValueError("job:{job_id} is not running"
                             .format(job_id=job_id))

        job = runners[job_id]
        lock.release()
        return job.get_report()


class JobNewHandler(JobHandler):
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
        timeout = data.get("timeout", DEFAULT_JOB_TIMEOUT)

        try:
            job = Job(str(uuid.uuid4()), data["data_source"],
                      data["models"], slack_channel, timeout)
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
            return

        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": job.to_dict()})


class JobDeleteHandler(JobHandler):
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})
            return

        try:
            logger.info("close running job:{job_id}"
                        .format(job_id=job_id))
            self.close_job(job_id)
            self.finish({"code": HTTP_OK,
                        "message": "OK"})
        except Exception as e:
            logger.error("close job:{job_id} failed:{err}"
                         .format(job_id=job_id, err=str(e)))
            self.finish({"code": HTTP_FAIL,
                         "message": "close job:{job_id} failed:{err}"
                        .format(job_id=job_id, err=str(e))})


class JobListHandler(JobHandler):
    def get(self):
        logger.info("list all running jobs")
        jobs = self.list_jobs()
        logger.info("running jobs:{jobs}"
                    .format(jobs=jobs))
        self.finish({"code": HTTP_OK,
                    "message": "OK",
                     "data": jobs})


class JobDetailHandler(JobHandler):
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})
            return

        try:
            logger.info("get job:{job_id} detail"
                        .format(job_id=job_id))
            job = self.job_detail(job_id)
            self.finish({"code": HTTP_OK,
                         "message": "OK",
                         "data": job})
        except Exception as e:
            logger.error("get job:{job_id} detail failed:{err}"
                         .format(job_id=job_id, err=str(e)))
            self.finish({"code": HTTP_FAIL,
                         "message": "get job:{job_id} detail failed:{err}"
                        .format(job_id=job_id, err=str(e))})


class JobReportHandler(JobHandler):
    def get(self, job_id):
        if job_id == "":
            logger.error("job id is required")
            self.finish({"code": HTTP_MISS_ARGS,
                         "message": "job id is required"})
            return

        try:
            logger.info("get job:{job_id} report"
                        .format(job_id=job_id))
            report = self.job_report(job_id)
            self.finish({"code": HTTP_OK,
                         "message": "OK",
                         "data": report})
        except Exception as e:
            logger.error("get job:{job_id} report failed:{err}"
                         .format(job_id=job_id, err=str(e)))
            self.finish({"code": HTTP_FAIL,
                         "message": "get job:{job_id} report failed:{err}"
                        .format(job_id=job_id, err=str(e))})



