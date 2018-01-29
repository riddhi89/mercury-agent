from mercury.common.clients.inventory import InventoryClient
from mercury.common.clients.rpc.frontend import RPCFrontEndClient
from mercury.common.exceptions import MercuryTransportError


def transceiver_decorator(f):
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        if result['error']:
            raise MercuryTransportError(f'[{self.service_name}]'
                                        f'Error communicating with service: '
                                        f'{result["message"]}')
        return result['message']
    return wrapper


class SimpleInventoryClient(InventoryClient):
    @transceiver_decorator
    def transceiver(self, payload):
        return super(InventoryClient, self).transceiver(payload)


class SimpleRPCFrontEndClient(RPCFrontEndClient):
    @transceiver_decorator
    def transceiver(self, payload):
        return super(RPCFrontEndClient, self).transceiver(payload)

