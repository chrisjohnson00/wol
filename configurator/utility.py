import os
import consul


def get_config(key, config_path=''):
    if os.environ.get(key):
        return os.environ.get(key)
    c = consul.Consul()
    if config_path:
        kv_key = f"{config_path}/{key}"
    else:
        kv_key = f"{key}"
    index, data = c.kv.get(kv_key)
    return data['Value'].decode("utf-8")
