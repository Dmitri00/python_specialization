import sys
import argparse
import os
import tempfile
import json

parser = argparse.ArgumentParser()
parser.add_argument('--key', type=str, required=True, default=None)
parser.add_argument('--value', type=str, default=None)

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')
    key = args.key
    value = args.value
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as storage_file:
            storage = json.load(storage_file)
    else:
        storage = {}
    if value is None:
        value = storage.get(key, None)
        if value is not None:
            print(', '.join(value))
    else:
        multi_value = storage.get(key, [])
        multi_value.append(value)
        storage[key] = multi_value
        with open(storage_path, 'w') as storage_file:
            json.dump(storage, storage_file)
