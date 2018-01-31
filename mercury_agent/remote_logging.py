import logging

from mercury.common.exceptions import MercuryGeneralException
from mercury.common.clients.router_req_client import RouterReqClient

LOG = logging.getLogger('')


class MercuryLogHandler(logging.Handler):
    def __init__(self, service_url, mercury_id=None):
        super(MercuryLogHandler, self).__init__()

        self.service_url = service_url
        self.__mercury_id = mercury_id

        self.client = RouterReqClient(self.service_url, linger=0,
                                      response_timeout=5)
        self.service_name = 'Logging Service'

    def emit(self, record):
        if not self.__mercury_id:
            return

        data = record.__dict__
        data.update({'mercury_id': self.__mercury_id})

        response = self.client.transceiver(data)
        if response.get('error'):
            raise MercuryGeneralException('Problem talking to logging service')

        # Close the socket
        # This is not efficient, I need to find a way to disconnect the socket
        # after it has gone idle.

        self.client.close()

    def set_mercury_id(self, mercury_id):
        self.__mercury_id = mercury_id
