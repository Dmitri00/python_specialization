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
        if ' ' in key:
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
        self.value = self.check_num(value)
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
        self.key = self.check_key(key)
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
    def __init__(self, key, value, timestamp):
        self.key = key
        self.value = value
        self.timestamp = timestamp
    @classmethod
    def from_str(cls, data_line):
        #import pdb; pdb.set_trace()
        data_line_splited = data_line.split(' ')
        if len(data_line_splited) != 3:
            raise ResponseError()
        try:
            key = data_line_splited[0]
            value = float(data_line_splited[1])
            timestamp = int(data_line_splited[2])
            return cls(key, value, timestamp)
        except ValueError:
            raise ResponseError()
    def __str__(self):
        fmt = '| {key:10} | {value:10.2f} | {ts:10d} |'
        return fmt.format(key=self.key, ts=self.timestamp, value=self.value)
    def __repr__(self):
        # according to task, value of 1 should be represented as str '1.0'
        # 4.654 - as '4.654'. str.format doesn't allow to format float this way in one line
        # that's why firstly value is converted to str via float.__str__ method
        fmt = '{key} {value:s} {ts:d}'
        return fmt.format(key=self.key, ts=self.timestamp, value=str(self.value))
class Response:
    RESPONSE_FORMAT = '{status}\n{data}\n\n'
    OK_MSG = 'ok\n\n'
    def __init__(self, is_ok, metrics, error_msg='wrong command'):
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
        not_empty_lines = filter(lambda x: len(x) > 0, data_lines)
        metrics.extend(list(map(Metric.from_str, not_empty_lines)))
        return metrics
    def __str__(self):
        if self.status:
            status = 'ok'   
            data = '\n'.join(map(repr, self.metrics))
        else:
            status = 'error'
            data = self.error_msg
        if self.status and len(data) == 0:
            return self.OK_MSG
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