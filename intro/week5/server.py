import asyncio
from protocol_classes import PutCmd, GetCmd, Metric, Response, ClientRequest
from protocol_classes import ServerError, ProtocolError
from bisect import bisect
class MetricList:
    def __init__(self):
        self.metric_list = []
    def add(self, metric):
        class ListCol:
            def __init__(self, list_, col):
                self.list_ = list_
                self.col = col
            def __getitem__(self, index):
                return self.list_[index][self.col]
        
        timestamp_col = 0
        list_col = ListCol(self.metric_list,timestamp_col)
        insert_pos = bisect(list_col, metric[timestamp_col])
        self.metric_list.insert(insert_pos, metric)
class ClientServerProtocol(asyncio.Protocol):
    metrics_db = {}
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        resp = self.process_data(data.decode())
        self.transport.write(resp.encode())
    def process_data(self,  cmd_str):
        try:
            first_space = cmd_str.index(' ') + 1
            data_end = cmd_str.index('\n')
            cmd_name = cmd_str[:first_space]
            data_str = cmd_str[first_space+1:data_end]

            client_request = ClientRequest(cmd_name, data_str)
            if client_request.cmd_class == PutCmd:
                return self.process_put(client_request)
            elif client_request.cmd_class == GetCmd:
                return self.process_get(client_request)
        except ValueError:
            return self.send_error()
        except ProtocolError:
            return self.send_error()

    def process_get(self, client_request):
        key = client_request.key
        
        if key in self.metrics_db:
            data = self.metrics_db[key]
        elif key == '*':
            data = self.metrics_db
        else:
            data = []
        is_ok = True
        return Response(is_ok, data)
    def process_put(self, put_cmd):
        
        if put_cmd.key in self.metrics_db:
            metrics_array = self.metrics_db[put_cmd.key]
            insert_pos = bisect(metrics_array, put_cmd.timestamp)
            value_col = 0
            timestamp_col = 1
            
            if metrics_array[insert_pos][timestamp_col] == put_cmd.timestamp:
                metrics_array[insert_pos][value_col] = put_cmd.value
            else:
                metrics_array.insert(insert_pos, [put_cmd.value, put_cmd.timestamp])
        else:
            self.metrics_db[put_cmd.key] = [[put_cmd.value, put_cmd.timestamp]]
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
        server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()