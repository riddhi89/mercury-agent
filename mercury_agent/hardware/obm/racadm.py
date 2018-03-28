from mercury.common.helpers import cli


class SimpleRACException(Exception):
    pass


class SimpleRAC(object):
    def __init__(self, path='racadm'):
        """

        :param path:
        """
        self.racadm_path = cli.find_in_path(path)
        if not self.racadm_path:
            raise SimpleRACException('Could not find racadm binary')

    def racadm(self, command):
        result = cli.run('sh {} {}'.format(self.racadm_path, command),
                         raise_exception=False, ignore_error=True)
        if result.returncode:
            raise SimpleRACException(
                'Error running racadm command: {}, code {}'.format(
                    command, result.returncode))

        return result.stdout

    @property
    def getsysinfo(self):
        """
        Simple 'parser' for getsysinfo command
        :return:
        """
        output = self.racadm('getsysinfo')
        sys_info = {}
        key = None
        for line in output.splitlines():
            if not line:
                continue
            if '=' not in line and line.strip()[-1] == ':':
                key = line[:-1]
                sys_info[key] = {}
                continue

            if key:
                sub_key, d = [term.strip() for term in line.split('=', 1)]
                if d == '::':  # :: seems to imply an empty field
                    d = None
                sys_info[key][sub_key] = d
        return sys_info
