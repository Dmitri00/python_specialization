class ClientError(Exception): pass
class ServerError(Exception): pass
class ProtocolError(ClientError, ServerError): pass
class CmdArgumentError(ProtocolError): pass
class ResponseError(ProtocolError): pass
class WrongCommandError(ProtocolError): pass
class WrongArgumentsError(ProtocolError): pass


class GeneralCmd:
    KEY_DELIM = '.'
    CMD_FORMAT = '{name:} {data:}\n'
    cmd_name = ''
    def check_str(self, key):
        if isinstance(key, str) and len(key) > 0:
            return key
        else:
            raise CmdArgumentError()
    # methods for constructor parameter's checks
    # 
    def check_key(self, key):
        """check that key is str"""
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
    # 
    def check_num(self, num):
        """type check for metric value """
        if isinstance(num, float) or isinstance(num, int):
            return num
        else:
            raise CmdArgumentError()
    #
    def check_timestamp(self, num):
        """type check for timestamp"""
        if isinstance(num, int) and num > 0:
            return num
        else:
            raise CmdArgumentError()
    # 
    def __str__(self):
        """serialization method. It concatenates parent field cmd_name and child data from str_data"""
        cmd_data = self._str_data()
        cmd_str = self.CMD_FORMAT.format(name=self.cmd_name, data=cmd_data)
        return cmd_str
    # 
    def _str_data(self):
        return ''
    
    # 
    def encode(self):
        """This wrapper was made to allow easy extension of encoding routine in the future"""
        return str(self).encode()
class PutCmd(GeneralCmd):
    cmd_name = 'put'
    def __init__(self, key, value, timestamp):
        self.key = self.check_key(key)
        self.value = '{:g}'.format(self.check_num(value))
        self.timestamp = self.check_timestamp(timestamp)
    @classmethod
    def from_str(cls, cmd_data):
        """method for server to parse txt line from client"""
        if not cmd_data.count(' ') == 2:
            raise CmdArgumentError
        key, value, timestamp = cmd_data.split()
        try:
            value = float(value)
            timestamp = int(timestamp)
        except ValueError:
            raise CmdArgumentError
        return PutCmd(key, value, timestamp)
    def _str_data(self):
        
        cmd_data = list(map(str, (self.key, self.value, self.timestamp)))
        cmd_data = ' '.join(cmd_data)
        return cmd_data

    def __eq__(self, other):
        """method for test purposes"""
        if self.key != other.key:
            return False
        elif self.timestamp != other.timestamp:
            return False
        elif self.value != other.value:
            return False
        else:
            return True
        

class GetCmd(GeneralCmd):
    cmd_name = 'get'
    def __init__(self, key='*'):
        self.key = self.check_str(key)
    @classmethod
    def from_str(cls, cmd_data):
        return GetCmd(cmd_data)
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
            raise ResponseError()
    def __str__(self):
        fmt = '| {key:10} | {ts:10d} | {value:10.2f} |'
        return fmt.format(key=self.key, ts=self.timestamp, value=self.value)
    def __repr__(self):
        fmt = '{key} {ts:d} {value:g}'
        return fmt.format(key=self.key, ts=self.timestamp, value=self.value)
class Response:
    RESPONSE_FORMAT = '{status}\n{data}\n\n'
    def __init__(self, is_ok, metrics, error_msg=''):
        self.status = is_ok
        if is_ok:
            self.metrics = metrics
            self.error_msg = ''
        else:
            if len(error_msg) == 0:
                raise ResponseError()
            self.error_msg = error_msg
            self.metrics = None
    @classmethod
    def from_str(cls, response_str):
        """method for client to parse response from server"""
        #import pdb; pdb.set_trace()
        response_splited = response_str.split('\n')
        if len(response_splited) < 3:
            raise ResponseError()
        response_splited = response_splited[:-2]
        status = response_splited[0]
        
        status = cls.check_status(status)
        msg = ''
        metrics = []
        
        if status:
            data_lines = response_splited[1:]
            metrics = cls.parse_data(data_lines)
            assert metrics is not None, 'Response class got none metrics from {:}'.format(response_splited)
        else:
            msg = response_splited[1]
        return Response(status, metrics, msg)
    @staticmethod 
    def check_status(status):
        if status == 'ok':
            return True
        elif status == 'error':
            return False
        else:
            raise ResponseError()
    @staticmethod
    def parse_data(data_lines):
        metrics = []
        metrics.extend(list(map(Metric, data_lines)))
        return metrics
    def __str__(self):
        if self.status:
            status = 'ok'
            data = '\n'.join(map(str, self.metrics))
        else:
            status = 'error'
            data = self.error_msg
        return self.RESPONSE_FORMAT.format(status=status, data=data)
    def encode(self):
        return str(self).encode()

class ClientRequest:
    commands = {'get': GetCmd,
                'put': PutCmd }
    def __init__(self, cmd_name, data_str):
        if cmd_name in self.commands:
            self.cmd_class = self.commands[cmd_name]
            self.cmd = self.cmd_class.from_str(data_str)
        else:
            raise WrongCommandError
