import json

import pytest

from mercury_api.exceptions import HTTPError
from mercury_api.app import app as mercury_app
from mercury_api.active.views import (
    ActiveComputerView,
    ActiveComputerQueryView,
)

from ..inventory.fixtures import test_mercury_id, inventory_patch


class TestActiveComputerView(object):

    view = ActiveComputerView()

    def test_get(self):
        with mercury_app.test_request_context():
            response = self.view.get()
            data = json.loads(response.data)
        assert data['items'][0]['mercury_id'] == test_mercury_id

    def test_get_one(self):
        with mercury_app.test_request_context():
            response = self.view.get(test_mercury_id)
            data = json.loads(response.data)
        assert data['mercury_id'] == test_mercury_id

    @pytest.mark.xfail(raises=HTTPError, strict=True)
    def test_get_one_error(self):
        with mercury_app.test_request_context():
            self.view.get(mercury_id='does-not-exist')


class TestActiveComputerQueryView(object):

    view = ActiveComputerQueryView()

    def test_post(self):
        data = {'query': {}}
        with mercury_app.test_request_context(data=json.dumps(data),
                                              method='POST',
                                              content_type='application/json'):
            response = self.view.post()
            data = json.loads(response.data)
        assert data['items'][0]['mercury_id'] == test_mercury_id
