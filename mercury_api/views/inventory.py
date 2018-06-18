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

import logging

from flask import Blueprint, request, jsonify

from mercury_api.exceptions import HTTPError
from mercury_api.decorators import validate_json, check_query
from mercury_api.views import (
    get_projection_from_qsa,
    get_paging_info_from_qsa,
    inventory_client,
)


log = logging.getLogger(__name__)
inventory_blueprint = Blueprint('inventory', __name__)


@inventory_blueprint.route('/computers',
                           methods=['GET'], strict_slashes=False)
def list_inventory():
    """
    Query the inventory client for device records with a given projection
    or get one by mercury_id.

    :return: List of inventory objects.
    """
    projection = get_projection_from_qsa()
    paging_info = get_paging_info_from_qsa()
    data = inventory_client.query(
        {},
        projection=projection,
        limit=paging_info['limit'],
        sort=paging_info['sort'],
        sort_direction=paging_info['sort_direction'],
        offset_id=paging_info['offset_id']
    )

    return jsonify(data)


@inventory_blueprint.route('/computers/<mercury_id>',
                           methods=['GET'], strict_slashes=False)
def get_inventory(mercury_id):
    """
    Get one inventory object by mercury_id.

    :param mercury_id: Device mercury id.
    :return: Inventory object.
    """
    projection = get_projection_from_qsa()
    data = inventory_client.get_one(mercury_id,
                                    projection=projection)
    if not data:
        message = 'mercury_id {} does not exist in inventory'
        raise HTTPError(message.format(mercury_id), status_code=404)

    return jsonify(data)


@validate_json
@check_query
@inventory_blueprint.route('/computers/query',
                           methods=['POST'], strict_slashes=False)
def query_inventory_devices():
    """
    Query inventory devices with a given projection.

    :return: List of inventory objects.
    """
    query = request.json.get('query')
    projection = get_projection_from_qsa()
    page_info = get_paging_info_from_qsa()
    log.debug('QUERY: {}'.format(query))

    data = inventory_client.query(
        query,
        projection=projection,
        limit=page_info['limit'],
        sort=page_info['sort'],
        sort_direction=page_info['sort_direction'],
        offset_id=page_info['offset_id'])
    return jsonify(data)


@validate_json
@check_query
@inventory_blueprint.route('/computers/count',
                           methods=['POST'], strict_slashes=False)
def count_devices():
    """
    Return the device count that matches the given projection.
    
    :return: dict
    """
    query = request.json.get('query')
    data = {'count': inventory_client.count(query)}
    return jsonify(data)
