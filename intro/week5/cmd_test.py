import unittest
from client import ClientError, GetCmd, PutCmd
import pdb
class CmdTest(unittest.TestCase):
    def test_get_cmd_bad_key(self):
        bad_keys = ['cpucpu', 'cpu cpu', 'cpu.cpu.cpu', None ]
        for bad_key in bad_keys:
            with self.assertRaises(ClientError):
                GetCmd(bad_key)
    def test_get_cmd_good_key(self):
        keys = ['cpu.usage', 'cpu.temp', 'mem.usage', '*']
        for key in keys:
            try:
                GetCmd(key)
            except ClientError:
                self.assertTrue(False)
    def test_put_cmd_bad_key(self):
        bad_keys = ['cpucpu', 'cpu cpu', 'cpu.cpu.cpu', None, '*']
        value = 2
        timestamp = 1
        for bad_key in bad_keys:
            with self.assertRaises(ClientError):
                PutCmd(bad_key, value, timestamp)
    def test_put_cmd_bad_timestamp(self):
        key = 'cpu.cpu'
        bad_stamps = [-100, -1, 0, None]
        value = 2
        for bad_stamp in bad_stamps:
            with self.assertRaises(ClientError):
                PutCmd(key, value, bad_stamp)
    def test_put_cmd_bad_value(self):
        key = 'cpu.cpu'
        timestamp = 132432 
        bad_values = ['434', 'fdf', '', None,2+3j]
        for bad_value in bad_values:
            with self.assertRaises(ClientError):
                PutCmd(key, bad_value, timestamp)
    def test_put_cmd_good_args(self):
        keys = ['cpu.usage', 'cpu.temp', 'mem.usage']
        timestamps = [132432 , 4324, 432432432]
        values = [1,2,35,2.0, -5.0, 1e6, -1e-5, -1e10] 
        for key in keys:
            for value in values:
                for timestamp in timestamps:
                    try:
                        PutCmd(key, value, timestamp)
                    except ClientError:
                        self.assertTrue(False)
    def test_put_cmd_str(self):
        key = 'cpu.cpu'
        value = 55.0
        timestamp = 543534
        cmd_str_true = 'put {:} {:} {:d}\n'.format(key, str(value), timestamp)
        #pdb.set_trace()
        put_cmd = PutCmd(key, value, timestamp)
        cmd_str_test = str(put_cmd)
        
        self.assertTrue(cmd_str_true == cmd_str_test)
    def test_get_cmd_str(self):
        key = 'cpu.cpu'
        cmd_str_true = 'get {:}\n'.format(key)
        #pdb.set_trace()
        get_cmd = GetCmd(key)
        cmd_str_test = str(get_cmd)
        self.assertTrue(cmd_str_true == cmd_str_test)
    def test_get_cmd_str_asterisk(self):
        key = '*'
        cmd_str_true = 'get {:}\n'.format(key)
        #pdb.set_trace()
        get_cmd = GetCmd(key)
        cmd_str_test = str(get_cmd)
        self.assertTrue(cmd_str_true == cmd_str_test)

        key = '*'
        cmd_str_true = 'get {:}\n'.format(key)
        #pdb.set_trace()
        get_cmd = GetCmd()
        cmd_str_test = str(get_cmd)
        self.assertTrue(cmd_str_true == cmd_str_test)


if __name__ == '__main__':
    unittest.main()
