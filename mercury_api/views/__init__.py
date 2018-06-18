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

import bson
import logging

from flask import request

from mercury_api.configuration import get_api_configuration
from mercury_api.mercury_clients import SimpleInventoryClient, \
    SimpleRPCFrontEndClient

log = logging.getLogger(__name__)
api_configuration = get_api_configuration()

inventory_url = api_configuration.api.inventory.inventory_router
rpc_url = api_configuration.api.rpc.rpc_router

inventory_client = SimpleInventoryClient(inventory_url,
                                         linger=0,
                                         response_timeout=15,
                                         raise_on_timeout=True)
rpc_client = SimpleRPCFrontEndClient(rpc_url,
                                     linger=0,
                                     response_timeout=5,
                                     raise_on_timeout=True)


def get_projection_from_qsa():
    """
    Gets the projection from the request url parameters and transforms 
    them into a dictionary.

    :return: dict
    """
    projection_keys = request.args.get('projection', '')
    projection = {}
    if projection_keys:
        for k in projection_keys.split(','):
            projection[k] = 1

    return projection or None


def get_paging_info_from_qsa():
    """
    Gets the paging delimiters from the url if any, otherwise return
    the defaults from the api configuration.

    :return: dict
    """
    delimiters = api_configuration.api.paging.to_dict()
    limit = request.args.get('limit')
    offset_id = request.args.get('offset_id')
    sort_direction = request.args.get('sort_direction')

    if limit and limit.isdigit():
        delimiters['limit'] = int(limit)

    if bson.ObjectId.is_valid(offset_id):
        delimiters['offset_id'] = offset_id

    try:
        delimiters['sort_direction'] = int(sort_direction)
    except (TypeError, ValueError):
        # None == TypeError, anything else == ValueError
        pass
    return delimiters


def get_limit_and_sort_direction():
    """
    Get the limit and sort direction from the paging method.
    
    :return: tuple
    """
    paging_data = get_paging_info_from_qsa()
    limit = paging_data.get('limit')
    sort_direction = paging_data.get('sort_direction')

    return limit, sort_direction
