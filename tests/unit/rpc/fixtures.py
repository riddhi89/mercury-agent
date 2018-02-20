import pytest


test_job_id = 'some-job-id'
test_task_id = 'some-task-id'


@pytest.fixture(autouse=True)
def rpc_patch(monkeypatch):
    def get_jobs(*args, **kwargs):
        response = {
            'items': [
                {'job_id': test_job_id}
            ]
        }
        return response

    def get_job(object, job_id, projection):
        if job_id == test_job_id:
            return {'job_id': test_job_id}
        return {}

    def get_job_status(object, job_id):
        if job_id == test_job_id:
            return {'job_id': test_job_id}
        return {}

    def get_job_tasks(object, job_id, projection):
        if job_id == test_job_id:
            response = {
                'items': [
                    {'task_id': test_task_id}
                ],
                'count': 1
            }
        else:
            response = {
                'items': [],
                'count': 0
            }
        return response

    def create_job(object, query, instruction):
        if not query:
            return {'job_id': test_job_id}
        return {}

    def get_task(object, task_id):
        if task_id == test_task_id:
            return {'task_id': test_task_id}
        return {}

    get_jobs_attr = 'mercury_api.views.RPCFrontEndClient.get_jobs'
    get_job_attr = 'mercury_api.views.RPCFrontEndClient.get_job'
    get_job_status_attr = 'mercury_api.views.RPCFrontEndClient.get_job_status'
    get_job_tasks_attr = 'mercury_api.views.RPCFrontEndClient.get_job_tasks'
    create_job_attr = 'mercury_api.views.RPCFrontEndClient.create_job'
    get_task_attr = 'mercury_api.views.RPCFrontEndClient.get_task'

    monkeypatch.setattr(get_jobs_attr, get_jobs)
    monkeypatch.setattr(get_job_attr, get_job)
    monkeypatch.setattr(get_job_status_attr, get_job_status)
    monkeypatch.setattr(get_job_tasks_attr, get_job_tasks)
    monkeypatch.setattr(create_job_attr, create_job)
    monkeypatch.setattr(get_task_attr, get_task)
