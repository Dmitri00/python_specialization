import unittest
from unittest.mock import patch
from client import Metric, Client, ClientError



class ClientTest(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('socket.socket')
        self.MockClass = self.patcher.start()
        sock_instance = self.MockClass.return_value
        server_response = 'ok\n\n'.encode()
        sock_instance.recv = unittest.mock.Mock(return_value=server_response)
    def tearDown(self):
        self.patcher.stop()
    #@patch('socket.socket')
    def test_get_cmd_bad_str_key(self):
        bad_keys = ['cpucpu', 'cpu cpu', 'cpu.cpu.cpu']
        client = Client()
        for bad_key in bad_keys:
            metrics = client.get(bad_key)
            self.assertTrue(metrics == {})
    #@patch('socket.socket')
    def test_get_cmd_good_key(self):
        keys = ['cpu.usage', 'cpu.temp', 'mem.usage', '*']
        client = Client()
        for key in keys:
            try:
                client.get(key)
            except ClientError:
                self.assertTrue(False)
    #@patch('socket.socket')
    def test_put_cmd_bad_key(self):
        bad_keys = ['cpucpu', 'cpu cpu', 'cpu.cpu.cpu', None, '*']
        value = 2
        timestamp = 1
        client = Client()
        for bad_key in bad_keys:
            with self.assertRaises(ClientError):
                client.put(bad_key, value, timestamp)
    #@patch('socket.socket')
    def test_put_cmd_bad_timestamp(self):
        key = 'cpu.cpu'
        bad_stamps = [-100, -1, 0]
        value = 2
        client = Client()
        for bad_stamp in bad_stamps:
            with self.assertRaises(ClientError):
                client.put(key, value, bad_stamp)
    #@patch('socket.socket')
    def test_put_cmd_bad_value(self):
        key = 'cpu.cpu'
        timestamp = 132432 
        bad_values = ['434', 'fdf', '', None,2+3j]
        client = Client()
        for bad_value in bad_values:
            with self.assertRaises(ClientError):
                #import pdb; pdb.set_trace()
                client.put(key, bad_value, timestamp)
    #@patch('socket.socket')
    def test_put_cmd_good_args(self):
        keys = ['cpu.usage', 'cpu.temp', 'mem.usage']
        timestamps = [132432 , 4324, 432432432]
        values = [1,2,35,2.0, -5.0, 1e6, -1e-5, -1e10] 
        client = Client()
        for key in keys:
            for value in values:
                for timestamp in timestamps:
                    try:
                        client.put(key, value, timestamp)
                    except ClientError:
                        self.assertTrue(False)
    #@patch('socket.socket')
    def test_get_sends_byte_str_command(self):
        key = 'cpu.cpu'
        cmd_bytes = 'get {}\n'.format(key).encode()
        client = Client()
        
        
        #import pdb; pdb.set_trace()
        client.get(key)

        sock_instance = self.MockClass.return_value
        sock_instance.connect.assert_called()
        
        first_call = 0
        positional_args = 0
        call_args = sock_instance.sendall.call_args_list[first_call][positional_args]
        sended_str = call_args[0]
        self.assertTrue(cmd_bytes == sended_str)
    
    #@patch('socket.socket')
    def test_put_sends_byte_str_command(self):
        key = 'cpu.cpu'
        value = 54.0
        timestamp = 5435433
        cmd_bytes = 'put {} {:} {:d}\n'.format(key, str(value), timestamp).encode()
        client = Client()
        
        #import pdb; pdb.set_trace()
        client.put(key, value, timestamp)

        sock_instance = self.MockClass.return_value
        sock_instance.connect.assert_called()
        
        first_call = 0
        positional_args = 0
        call_args = sock_instance.sendall.call_args_list[first_call][positional_args]
        sended_str = call_args[0]
        #import pdb; pdb.set_trace()
        self.assertTrue(cmd_bytes == sended_str)
    def test_get_parses_empty_metrics(self):
        key = '*'
        client = Client()

        
        server_response = 'ok\n\n'.encode()
        sock_instance = self.MockClass.return_value
        sock_instance.recv = unittest.mock.Mock(return_value=server_response)

        metrics_expected = {}
        
        #import pdb; pdb.set_trace()
        metrics_received = client.get(key)
        self.assertTrue(metrics_expected == metrics_received)
    def test_get_parses_metrics(self):
        key = '*'
        client = Client()

        
        server_response = 'ok\ncpu.cpu 5 543543\ncpu.usage 3 4354325\n\n'.encode()
        sock_instance = self.MockClass.return_value
        sock_instance.recv = unittest.mock.Mock(return_value=server_response)

        metrics_expected = {'cpu.cpu': [(543543, 5)], 'cpu.usage': [(4354325, 3)]}
        
        #import pdb; pdb.set_trace()
        metrics_received = client.get(key)
        self.assertTrue(metrics_expected == metrics_received)


    def test_get_parses_metrics2(self):
        key = '*'
        client = Client()

        
        server_response = 'ok\npalm.cpu 10.5 1501864247\neardrum.cpu 15.3 1501864259\npalm.cpu 8.3 1501864340\neardrum.memory 200 1501861111\n\n'.encode()
        sock_instance = self.MockClass.return_value
        sock_instance.recv = unittest.mock.Mock(return_value=server_response)

        metrics_expected = {'palm.cpu': [
                                (1501864247, 10.5), 
                                (1501864340, 8.3)], 
                            'eardrum.memory': [(1501861111, 200)],
                            'eardrum.cpu': [(1501864259, 15.3)]
                            }

        metrics_received = client.get(key)
        self.assertTrue(metrics_expected == metrics_received)
        

if __name__ == '__main__':
    unittest.main()