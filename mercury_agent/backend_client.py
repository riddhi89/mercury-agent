from mercury_agent.configuration import get_configuration
from mercury.common.clients.rpc.backend import BackEndClient


# Private
__backend_client = None


def get_backend_client():
    # TODO: Trying this out, 0mq says it is ok
    global __backend_client
    if not __backend_client:
        __backend_client = BackEndClient(
            get_configuration().agent.remote.backend_url)
    return __backend_client
