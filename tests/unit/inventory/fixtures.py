import pytest


test_mercury_id = 'some-mercury-id'


@pytest.fixture(autouse=True)
def inventory_patch(monkeypatch):
    def query(*args, **kwargs):
        response = {
            'items': [
                {'mercury_id': test_mercury_id}
            ]
        }
        return response

    def get_one(object, device_query, projection):
        response = {}
        if isinstance(device_query, dict):
            if device_query.get('mercury_id') == test_mercury_id:
                response = {'mercury_id': test_mercury_id}
        elif device_query == test_mercury_id:
            response = {'mercury_id': test_mercury_id}
        return response

    def count(*args, **kwargs):
        query_response = query(*args, **kwargs)
        return len(query_response.get('items'))

    query_attribute = 'mercury_api.views.InventoryClient.query'
    get_one_attribute = 'mercury_api.views.InventoryClient.get_one'
    count_attribute = 'mercury_api.views.InventoryClient.count'

    monkeypatch.setattr(query_attribute, query)
    monkeypatch.setattr(get_one_attribute, get_one)
    monkeypatch.setattr(count_attribute, count)
