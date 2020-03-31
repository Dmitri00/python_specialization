import asyncio
from bisect import bisect
from collections import namedtuple

from protocol_classes import (ClientRequest, GetCmd, Metric, ProtocolError,
                              PutCmd, Response, ServerError)


class MetricList(list):
    """class contains list of objects with fields value and timestamp"""
    value_col = 0
    timestamp_col = 1
    # Namedtuple is used in order to make tuple (value, timestamp) order-invariant
    MetricPair = namedtuple('MetricPair', ('value', 'timestamp'))
    def add(self, timestamp, value):
        class ListCol:
            def __init__(self, list_, col):
                self.list_ = list_
                self.col = col
            def __getitem__(self, index):
                return self.list_[index][self.col]
            def __len__(self):
                return len(self.list_)
            
        
        #super_list = super()
        list_col = ListCol(self,self.timestamp_col)
        insert_pos = bisect(list_col, timestamp)

        new_metric = self.MetricPair(value, timestamp)
        if insert_pos == 0:
            self.insert(0, new_metric)
        elif self[insert_pos - 1].timestamp == timestamp:
            self[insert_pos - 1] = new_metric
        else:
            self.insert(insert_pos, new_metric)
class MetricsDict(dict):
    """contains dict of str key in namedtuple with fields value and timestamp"""
    def get_metric_lines(self, key=None):
        metric_lines = []
        if key is not None:
            converting_metrics = [(key, self[key])]
        else:
            converting_metrics = self.items()
        for metric_key, metrics in converting_metrics:
            # don't unpack fields in for-expression, because it's not order-invariant
            for metric_pair in metrics:
                line = Metric(metric_key, metric_pair.value, metric_pair.timestamp)
                metric_lines.append(line)
        return metric_lines

class ClientServerProtocol(asyncio.Protocol):
    metrics_db = MetricsDict()
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = self.process_data(data.decode())
        self.transport.write(resp.encode())
    def process_data(self,  cmd_str):
        #import pdb; pdb.set_trace()
        try:
            first_space = cmd_str.index(' ')
            data_end = cmd_str.index('\n')
            cmd_name = cmd_str[:first_space]
            data_str = cmd_str[first_space+1:data_end]
            data_str = data_str.strip()

            client_request = ClientRequest(cmd_name, data_str)
            if client_request.cmd_class == PutCmd:
                return self.process_put(client_request.cmd)
            elif client_request.cmd_class == GetCmd:
                return self.process_get(client_request.cmd)
        except ValueError:
            return self.send_error()
        except ProtocolError:
            return self.send_error()

    def process_get(self, get_cmd):
        key = get_cmd.key
        # get list of Metric objects
        if key in self.metrics_db:
            metrics = self.metrics_db.get_metric_lines(key)
        elif key == '*':
            metrics = self.metrics_db.get_metric_lines()
        else:
            metrics = []
        is_ok = True
        return Response(is_ok, metrics)
    def process_put(self, put_cmd):
        if put_cmd.key not in self.metrics_db:
            self.metrics_db[put_cmd.key] = MetricList()

        metrics_list = self.metrics_db[put_cmd.key]     
        metrics_list.add(put_cmd.timestamp, put_cmd.value)

        is_ok = True
        empty_data = []
        return Response(is_ok, empty_data)
    def send_error(self):
        is_ok = False
        empty_data = []
        error_msg = 'wrong command'
        return Response(is_ok, empty_data, error_msg)
        
        



def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
