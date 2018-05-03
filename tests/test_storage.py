# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
import os
import tempfile

from oasis.storage import new_sqlite_storage
from oasis.libs.log import logger


class TestSQliteStorage(unittest.TestCase):

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp()
        self.sqlite_storage = new_sqlite_storage(self.db_path)

        self.model_template = {
            'name': 'iForest',
            'config': 'test-config-1'
        }

        self.model_instance = {
            'model': 'iForest',
            'job_id': 1,
            'report': 'test-report-1',
            'status': 'running'
        }

        self.job = {
            'data_source': 'test-data-source',
            'models': 'iForest',
            'timeout': '4h',
            'slack_channel': 'oasis-channel',
            'reports': 'test-report-1',
            'model_instance_ids': '1',
            'status': 'running',
            'api_models_config': ''
        }

    def tearDown(self):
        os.unlink(self.db_path)

    def test_sqlite_storage(self):
        logger.info("start to test sqlite storage")

        logger.info("test set job")
        self._testSetJob()

        logger.info("test set model template")
        self._testSetModelTemplate()

        logger.info("test set model instance")
        self._testSetModelInstance()

        logger.info("test load job")
        self._testLoadJob()

        logger.info("test load model template")
        self._testLoadModelTemplate()

        logger.info("test load model instance")
        self._testLoadModelInstance()

    def _testSetJob(self):
        self.sqlite_storage.set_job(self.job)
        self.job['id'] = 1
        self.assertDictEqual(self.job, self.sqlite_storage.get_job(1))

        self.job['slack_channel'] = 'oasis-channel-1'
        self.sqlite_storage.set_job(self.job)
        new_job = self.sqlite_storage.get_job(self.job.get('id'))
        self.assertEqual(self.job['slack_channel'], new_job.get('slack_channel'))

    def _testSetModelTemplate(self):
        self.sqlite_storage.set_model_template(self.model_template)
        self.model_template['id'] = 1
        self.assertDictEqual(self.model_template,
                             self.sqlite_storage.get_model_template(self.model_template['name']))

        self.model_template['config'] = 'test-config-2'
        self.sqlite_storage.set_model_template(self.model_template)
        new_model_template = self.sqlite_storage.get_model_template(self.model_template.get('name'))
        self.assertEqual(self.model_template['config'], new_model_template.get('config'))

    def _testSetModelInstance(self):
        self.sqlite_storage.set_model_instance(self.model_instance)
        self.model_instance['id'] = 1
        self.assertDictEqual(self.model_instance,
                             self.sqlite_storage.get_model_instance(self.model_instance['id']))

        self.model_instance['report'] = 'test-report-2'
        self.sqlite_storage.set_model_instance(self.model_instance)
        new_model_instance = self.sqlite_storage.get_model_instance(self.model_instance.get('id'))
        self.assertEqual(self.model_instance['report'], new_model_instance.get('report'))

    def _testLoadJob(self):
        jobs = self.sqlite_storage.list_jobs()
        self.assertEqual(1, len(jobs))

    def _testLoadModelTemplate(self):
        templates = self.sqlite_storage.list_model_templates()
        self.assertEqual(1, len(templates))

    def _testLoadModelInstance(self):
        instances = self.sqlite_storage.list_model_instances()
        self.assertEqual(1, len(instances))


if __name__ == "__main__":
    unittest.main()

