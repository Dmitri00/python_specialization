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
        return str(data)
    
        



        
        


loop = asyncio.get_event_loop()
coro = loop.create_server(
    ClientServerProtocol,
    '127.0.0.1', 8181
)

server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()