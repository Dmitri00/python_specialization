import socket
from contextlib import closing
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
        data_line_splited = data_line.split(' ')
        if len(data_line_splited) != 3:
            raise ResponseError()
        try:
            self.key = data_line_splited[0]
            self.value = float(data_line_splited[1])
            self.timestamp = int(data_line_splited[2])
        except ValueError:
            raise ClientError()
    def __str__(self):
        fmt = '| {key:10} | {ts:10d} | {value:10.2f} |'
        return fmt.format(key=self.key, ts=self.timestamp, value=self.value)
class Response:
    def __init__(self, response):
        #import pdb; pdb.set_trace()
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
    def __init__(self, ip='127.0.0.1', port=8888, timeout=15):
        self.server_ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout is not None:
            self.sock.settimeout(self.timeout)
        self._connect()
    def put(self, key, value, timestamp): 
        put_cmd = PutCmd(key, value, timestamp)
        with closing(self._connect()):
            self.sock.sendall(str(put_cmd).encode())
    def _send_recv(self, request):
        response = bytearray()
        end_symb = '\n\n'.encode()
        buf_size = 4096
        try:
            self.sock.sendall(request)
            
            chunk = self.sock.recv(buf_size)
            response.extend(chunk)
            while chunk[-2:] != end_symb:
                chunk = self.sock.recv(buf_size)
                response.extend(chunk)
        except socket.timeout:
            raise ClientError('Exceed timeout on send')
        return response

    def get(self, key): 
        get_cmd = GetCmd(key)
        response = self._send_recv(str(get_cmd).encode())
        response_obj = Response(response.decode())
        if not response_obj.status:
            raise ClientError(response_obj.msg)
        metrics_dict = dict()

        #import pdb; pdb.set_trace()
        for metric in response_obj.metrics:
            
            metric_instance = (metric.timestamp, metric.value)
            if metric.key in metrics_dict:
                metrics_dict[metric.key] = metrics_dict[metric.key].append(metric_instance)
            else:
                metrics_dict[metric.key] = [metric_instance]
        return metrics_dict


    def _connect(self): 
        try:
            self.sock.connect((self.server_ip, self.port))
        except socket.timeout:
            raise ClientError('Exceed timeout on connect')
        return self.sock


