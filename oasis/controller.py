# -*- coding: utf-8 -*-

from __future__ import absolute_import

from Queue import Queue, Empty
from threading import Event, Thread
from pytimeparse.timeparse import timeparse
from oasis.libs.log import logger
from oasis.libs.iexceptions import (
    NewJobException,
    TaskTypeNotSupportedException,
    JobNotRunningException,
)
from oasis.job import (
    Job,
    JOB_ERROR,
    JOB_FINISHED,
    JOB_STOPPED
)

PENDING_SIZE_LIMIT = 16
RUNNING_SIZE_LIMIT = 8

JOB_SCHEDULE_INTERVAL = '1m'

JOB_CLEAN_LIST = [JOB_ERROR, JOB_STOPPED, JOB_FINISHED]


class Controller(object):
    def __init__(self, storage):
        self.storage = storage
        self.queue = Queue(maxsize=PENDING_SIZE_LIMIT)
        self.jobs = dict()
        self._exit = False
        self.event = Event()

        t = Thread(target=self.run)
        t.start()

    def run_job(self, job):
        logger.info("add new job: job-{id} to tasks queue"
                    .format(id=job.get('id')))
        try:
            self.new_task(Task(START_JOB, job))
        except Exception as e:
            logger.error("add new job: {job} failed: {err}".format(job=job, err=str(e)))
            raise NewJobException(job, str(e))

    def stop_job(self, job):
        logger.info("add stop job: job-{id} to tasks queue"
                    .format(id=job.get('id')))
        self.new_task(Task(STOP_JOB, job))

    def new_task(self, task):
        self.queue.put(task)

    def run(self):
        logger.info("start to run collector")

        while not self._exit:
            self.schedule_task()
            self.clean()

            self.event.wait(timeparse(JOB_SCHEDULE_INTERVAL))

    def close(self):
        logger.info("stop collector !")
        self._exit = True
        self.event.set()

        for job_id, job in self.jobs.items():
            job.close()

    def schedule_task(self):
        if len(self.jobs) >= RUNNING_SIZE_LIMIT:
            logger.warn("the number of tasks allowed to run exceeded the limit.")
            return
        try:
            task = self.queue.get_nowait()
        except Empty:
            logger.info("the queue of tasks is empty, skip schedule")
            return
        else:
            if task.typ == START_JOB:
                self.start_job_handler(task.job)
            elif task.typ == STOP_JOB:
                self.stop_job_handler(task.job)
            else:
                raise TaskTypeNotSupportedException(task)

    def start_job_handler(self, job):
        logger.info("run job: {job}".format(job=job))

        if job.get('id') in self.jobs.keys():
            logger.warn("the job is running")
            return
        job_instance = Job(self.storage, job)

        try:
            if not job_instance.valid():
                logger.error("the job is invalid")
                job_instance.update_status(JOB_ERROR)
                return

            self.jobs[job.get('id')] = job_instance

            t = Thread(target=job_instance.run)
            t.start()
        except Exception as e:
            logger.error("start job: {job} error: {err}"
                         .format(job=job, err=str(e)))
            logger.exception("Exception Logged")

    def stop_job_handler(self, job):
        logger.info("stop job: {job_id}".format(job_id=job.id))
        job_instance = self.jobs.get(job.get('id'))

        try:
            if job_instance is None:
                raise JobNotRunningException(job)

            t = Thread(target=job_instance.close)
            t.start()
        except Exception as e:
            logger.error("stop job: {job} error: {err}"
                         .format(job=job, err=str(e)))
            logger.exception("Exception Logged")

    def clean(self):
        delete_ids = []

        for job_id, job in self.jobs.items():
            status = job.status
            if status in JOB_CLEAN_LIST:
                delete_ids.append(job_id)

        for job_id in delete_ids:
            del self.jobs[job_id]


START_JOB = "start"
STOP_JOB = "stop"


class Task(object):
    def __init__(self, typ, job):
        self.typ = typ
        self.job = job





