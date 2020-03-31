import unittest
from protocol_classes import Response, Metric, GetCmd, PutCmd, ClientError
from client import Client
from server import run_server
import threading

class ServerTest(unittest.TestCase):
    host = '127.0.0.1'
    port = 8880
    timeout = 5
    def test_one_client_connects(self):
        no_exception = False
        Client(self.host, self.port, timeout=5)
        no_exception = True
        self.assertTrue(no_exception)
    def test_many_clients_connect(self):
        for i in range(20):
            self.test_one_client_connects()
    def test_get_same_key_two_clients(self):
        client1 = Client(self.host, self.port, timeout=5)
        client2 = Client(self.host, self.port, timeout=5)
        command = 'some_key'
        data_1 = None
        data_2 = None
        try:
            data_1 = client1.get(command)
            data_2 = client1.get(command)
        except ClientError:
            print('Сервер вернул ответ на валидный запрос, который клиент определил, '
                'как не корректный.. ')
        except BaseException as err:
            print(f"Сервер должен поддерживать соединение с клиентом между запросами, "
                f"повторный запрос к серверу завершился ошибкой: {err.__class__}: {err}")
            sys.exit(1)
        
        self.assertTrue(data_1 == data_2 == {})
    def test_get_same_key_two_clients(self):
        client1 = Client(self.host, self.port, timeout=5)
        client2 = Client(self.host, self.port, timeout=5)
        command = 'some_key'
        data_1 = None
        data_2 = None
        try:
            data_1 = client1.get(command)
            data_2 = client1.get(command)
        except ClientError:
            print('Сервер вернул ответ на валидный запрос, который клиент определил, '
                'как не корректный.. ')
        except BaseException as err:
            self.assertTrue(False, f"Сервер должен поддерживать соединение с клиентом между запросами, "
                f"повторный запрос к серверу завершился ошибкой: {err.__class__}: {err}")

        
        self.assertTrue(data_1 == data_2 == {})
    def test_laod_data_read_data(self):
        client1 = Client(self.host, self.port, timeout=5)
        client2 = Client(self.host, self.port, timeout=5)
        try:
            client1.put("k.1", 0.25, timestamp=1)
            client2.put("k.1", 2.156, timestamp=2)
            client1.put("k.1", 0.35, timestamp=3)
            client2.put("k.2", 30, timestamp=4)
            client1.put("k.2", 40, timestamp=5)
            client1.put("k.2", 41, timestamp=5)
        except Exception as err:
            self.assertTrue(False, f"Ошибка вызова client.put(...) {err.__class__}: {err}")

        expected_metrics = {
            "k.1": [(1, 0.25), (2, 2.156), (3, 0.35)],
            "k.2": [(4, 30.0), (5, 41.0)],
        }
        #import pdb; pdb.set_trace()
        metrics = client1.get("*")
        self.assertTrue(metrics == expected_metrics)

        expected_metrics = {"k.2": [(4, 30.0), (5, 41.0)]}
        metrics = client2.get("k.2")
        self.assertTrue(metrics == expected_metrics)

        expected_metrics = {}
        metrics = client1.get("k.3")
        self.assertTrue(metrics == expected_metrics)
        
        
    
