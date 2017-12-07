import json

import pytest

from mercury_api.exceptions import HTTPError
from mercury_api.app import app as mercury_app
from mercury_api.rpc.views import (
    JobView,
    JobStatusView,
    JobTaskView,
    TaskView,
)

from .fixtures import rpc_patch, test_job_id, test_task_id


class TestJobView(object):

    view = JobView()

    def test_get(self):
        with mercury_app.test_request_context():
            response = self.view.get()
            data = json.loads(response.data)
        assert data['items'][0]['job_id'] == test_job_id

    def test_get_one(self):
        with mercury_app.test_request_context():
            response = self.view.get(job_id=test_job_id)
            data = json.loads(response.data)
        assert data['job_id'] == test_job_id

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_get_one_error(self):
        with mercury_app.test_request_context():
            self.view.get(job_id='does-not-exist')

    def test_post(self):
        data = {'instruction': {}, 'query': {}}
        with mercury_app.test_request_context(data=json.dumps(data),
                                              method='POST',
                                              content_type='application/json'):
            response = self.view.post()
            data = json.loads(response.data)
        assert data['job_id'] == test_job_id

    @pytest.mark.xfail(raises=HTTPError)
    def test_post_instruction_error(self):
        data = {'query': {}}
        with mercury_app.test_request_context(data=json.dumps(data),
                                              method='POST',
                                              content_type='application/json'):
            self.view.post()

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_post_query_error(self):
        data = {'instruction': {}, 'query': {'some-silly-query': 123}}
        with mercury_app.test_request_context(data=json.dumps(data),
                                              method='POST',
                                              content_type='application/json'):
            self.view.post()


class TestJobStatusView(object):

    view = JobStatusView()

    def test_get_one(self):
        with mercury_app.test_request_context():
            response = self.view.get(job_id=test_job_id)
            data = json.loads(response.data)
        assert data['job_id'] == test_job_id

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_get_one_error(self):
        with mercury_app.test_request_context():
            self.view.get(job_id='does-not-exist')


class TestJobTaskView(object):

    view = JobTaskView()

    def test_get_one(self):
        with mercury_app.test_request_context():
            response = self.view.get(job_id=test_job_id)
            data = json.loads(response.data)
        assert data['count'] == 1

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_get_one_error(self):
        with mercury_app.test_request_context():
            self.view.get(job_id='does-not-have-tasks')


class TestTaskView(object):

    view = TaskView()

    def test_get_one(self):
        with mercury_app.test_request_context():
            response = self.view.get(task_id=test_task_id)
            data = json.loads(response.data)
        assert data['task_id'] == test_task_id

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_get_one_error(self):
        with mercury_app.test_request_context():
            self.view.get(task_id='does-not-exist')
