from json import dumps
from functools import wraps
def to_json(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        ret_val = func(*args, **kwargs)
        return dumps(ret_val)
    return wrapped

@to_json
def get_data():
    """
    >>> get_data()
    '{"data": 1}'
    
    Returns:
        [type] -- [description]
    """
    return {'data': 1}