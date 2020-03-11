import socket
"""
sock = socket.socket()
sock.bind()
sock.list()
conn, addr = sock.accept()
conn.recv

sock = socket.socket()
sock.connect()
sock.sendall()
sock.close()
"""
class ClientError(Exception): pass
class CmdArgumentError(ClientError): pass
class ResponseError(ClientError): pass

class Cmd:
    KEY_DELIM = '.'
    CMD_FORMAT = '{name:} {data:}\n'
    cmd_name = ''
    def check_str(self, key):
        if isinstance(key, str) and len(key) > 0:
            return key
        else:
            raise CmdArgumentError()
    def check_key(self, key):
        key = self.check_str(key)
        try:
            key.index(self.KEY_DELIM)
        except ValueError:
            raise CmdArgumentError()
        if key.count('.') > 1:
            raise CmdArgumentError()
        server, metric = key.split(self.KEY_DELIM)
        if not server.isalnum() or not metric.isalnum():
            raise CmdArgumentError()
        return key
    def check_num(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return num
        else:
            raise CmdArgumentError()
    def check_timestamp(self, num):
        if isinstance(num, int) and num > 0:
            return num
        else:
            raise CmdArgumentError()
    def _str_data(self):
        return ''
    def __str__(self):
        cmd_data = self._str_data()
        cmd_str = self.CMD_FORMAT.format(name=self.cmd_name, data=cmd_data)
        return cmd_str
class PutCmd(Cmd):
    cmd_name = 'put'
    def __init__(self, key, value, timestamp):
        self.key = self.check_key(key)
        self.value = float(self.check_num(value))
        self.timestamp = self.check_timestamp(timestamp)
    def _str_data(self):
        cmd_data = list(map(str, (self.key, self.value, self.timestamp)))
        cmd_data = ' '.join(cmd_data)
        return cmd_data
    def __eq__(self, other):
        if self.key != other.key:
            return False
        elif self.timestamp != other.timestamp:
            return False
        elif self.value != other.value:
            return False
        else:
            return True

class GetCmd(Cmd):
    cmd_name = 'get'
    def __init__(self, key='*'):
        self.key = self.check_key(key)
    def check_key(self, key):
        if key == '*':
            return key
        else:
            return super().check_key(key)
    def _str_data(self):
        return self.key
    def __eq__(self, other):
        if self.key != other.key:
            return False
        else:
            return True
class Metric:
    def __init__(self, data_line):
        data_line_splitted = data_line.split(' ')
        if len(data_line_splitted) != 3:
            raise ResponseError()
        try:
            self.key = str(data_line)[0]
            self.value = float(data_line[1])
            self.timestamp = int(data_line[2])
        except ValueError:
            raise ClientError()
class Response:
    def __init__(self, response):
        response_splited = response.split('\n')
        if len(response_splited) < 3:
            raise ResponseError()
        response_splited = response_splited[:-2]
        status = response_splited[0]
        
        self.status = self.check_status(status)
        self.msg = None
        self.metrics = None
        if self.status:
            data_lines = response_splited[1:]
            self.metrics = self.parse_data(data_lines)
        else:
            self.msg = response_splited[1]
            
    def check_status(self, status):
        if status == 'ok':
            return True
        elif status == 'error':
            return False
        else:
            raise ResponseError()
    def parse_data(self, data_lines):
        metrics = list(map(Metric, data_lines))
        return metrics

class Client:
    def __init__(self, ip='127.0.0.1', port='8888', timeout=15): pass

    def put(self, key, value, timestamp): pass
    def get(self, key): pass

    def _buld_get(self, key, value, timestamp): pass
    def _build_put(self, key): pass


