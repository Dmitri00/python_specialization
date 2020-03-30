import socket
import time
from contextlib import closing
from protocol_classes import PutCmd, GetCmd, Metric, Response
from protocol_classes import ClientError, ResponseError, CmdArgumentError
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


class Client:
    def __init__(self, ip='127.0.0.1', port=8888, timeout=None):
        self.server_ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self._connect()
    def put(self, key, value, timestamp=None): 
        if timestamp is None:
            timestamp = int(time.time())
        put_cmd = PutCmd(key, value, timestamp)
        response = self._send_recv(put_cmd.encode())
        response_obj = Response.from_str(response.decode())
        if not response_obj.status:
            raise ClientError(response_obj.msg)
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
        response = self._send_recv(get_cmd.encode())
        response_obj = Response.from_str(response.decode())
        if not response_obj.status:
            raise ClientError(response_obj.msg)
        metrics_dict = dict()


        for metric in response_obj.metrics:
            metric_instance = (metric.timestamp, metric.value)
            if metric.key in metrics_dict:
                #metrics_list = metrics_dict[metric.key]
                #metrics_list.append(metric_instance)
                metrics_dict[metric.key].append(metric_instance)
            else:
                metrics_dict[metric.key] = [metric_instance]
        for key, metrics in metrics_dict.items():
            assert metrics is not None
            metrics_dict[key] = sorted(metrics, key=lambda x:x[0])
        
        return metrics_dict


    def _connect(self): 
        try:
            self.sock.connect((self.server_ip, self.port))
        except socket.timeout:
            raise ClientError('Exceed timeout on connect')
        return self.sock


