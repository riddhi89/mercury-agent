# Copyright 2017 Ruben Quinones (ruben.quinones@rackspace.com)
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from flask import Blueprint, request, jsonify

from mercury_api.views import get_projection_from_qsa, rpc_client
from mercury_api.exceptions import HTTPError
from mercury_api.decorators import validate_json, check_query


rpc_blueprint = Blueprint('rpc', __name__)


@validate_json
@check_query
@rpc_blueprint.route('/jobs', methods=['POST'], strict_slashes=False)
def create_job():
    """
    Creates a job with the given instructions.

    :return: The created job id.
    """
    instruction = request.json.get('instruction')
    if not isinstance(instruction, dict):
        raise HTTPError(
            'Command is missing from request or is malformed',
            status_code=400)
    query = request.json.get('query')
    if not isinstance(query, dict):
        raise HTTPError(
            'Query is missing from request or is malformed',
            status_code=400)
    job_id = rpc_client.create_job(query, instruction)

    if not job_id:
        raise HTTPError(
            'Query did not match any active agents', status_code=404)
    return jsonify(job_id)


@rpc_blueprint.route('/jobs', methods=['GET'], strict_slashes=False)
def list_jobs():
    """
    Query the RPC service for job records with a given projection.

    :return: List of job objects. 
    """
    projection = get_projection_from_qsa() or {'instruction': 0}
    data = rpc_client.get_jobs(projection)

    return jsonify(data)


@rpc_blueprint.route('/jobs/<job_id>', methods=['GET'], strict_slashes=False)
def get_job(job_id):
    """
    Get the job status by job_id.

    :param job_id: RPC job id, default is None.
    :return: Job object. 
    """
    projection = get_projection_from_qsa()
    data = rpc_client.get_job(job_id, projection)
    if not data:
        raise HTTPError(
            'Job {} does not exist'.format(job_id), status_code=404)

    return jsonify(data)


@rpc_blueprint.route('/jobs/<job_id>/status',
                     methods=['GET'], strict_slashes=False)
def get_job_status(job_id):
    """
    Get one Job by job_id.

    :param job_id: RPC job id.
    :return: Job status dictionary. 
    """
    job = rpc_client.get_job_status(job_id)
    if not job:
        raise HTTPError(
            'Job {} does not exist'.format(job_id), status_code=404)
    return jsonify(job)


@rpc_blueprint.route('/jobs/<job_id>/tasks',
                     methods=['GET'], strict_slashes=False)
def get_job_task(job_id):
    """
    Query the RPC service for tasks associated to a given job_id.

    :param job_id: RPC job id.
    :return: List of task objects. 
    """
    projection = get_projection_from_qsa()
    tasks = rpc_client.get_job_tasks(job_id, projection)
    if tasks['count'] == 0:
        raise HTTPError(
            'No tasks exist for job {}'.format(job_id), status_code=404)
    return jsonify(tasks)


@rpc_blueprint.route('/task/<task_id>',
                     methods=['GET'], strict_slashes=False)
def get_task(task_id):
    """
    Query the RPC service for a task record with a given task_id.

    :param task_id: RPC task id.
    :return: Sinle RPC task object. 
    """
    task = rpc_client.get_task(task_id)
    if not task:
        raise HTTPError('Task not found', status_code=404)
    return jsonify(task)
