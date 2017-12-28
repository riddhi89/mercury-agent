
from mercury_agent.inspector.inspectors import expose
from mercury_agent.inspector.hwlib.meminfo import parse_meminfo


@expose('mem')
def memory_inspector():
    return parse_meminfo()


if __name__ == '__main__':
    import pprint

    pprint.pprint(memory_inspector())
