from wakeonlan import send_magic_packet  # https://pypi.org/project/wakeonlan/
import socket
import time
from configurator.utility import get_config
import logging
import redis
import json


def process_message(message):
    # message.message = { 'name': 'nfs2',
    #                     'mac_address': 'b8:ca:3a:5d:28:b8',
    #                     'ip': '192.168.1.132',
    #                     'port': '22'
    #                   }
    logging.info("Sending magic packet")
    message_body = message.message
    logging.debug(f"Sending broadcast to {message_body['mac_address']}")
    send_magic_packet(message_body['mac_address'])
    logging.info(f"Checking every 1m if {message_body['ip']}:{message_body['port']} is open")
    ready = is_open(message_body['ip'], message_body['port'])
    while not ready:
        logging.info(f"{message_body['ip']}:{message_body['port']} is not yet open, checking again in 60s")
        ready = is_open(message_body['ip'], message_body['port'])
        time.sleep(60)
    logging.info(f"{message_body['name']} is up and ready for business")
    return True


def is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception:
        logging.exception(f"Unable to connect to {ip}:{port}")
        return False


def main():
    redis_conn = redis.Redis(host=get_config('REDIS_HOST'), charset="utf-8", decode_responses=True)
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(get_config('REDIS_CHANNEL'))
    logging.info(f"Subscribed to {get_config('REDIS_CHANNEL')}")
    for message in pubsub.listen():
        if message.get("type") == "message":
            data = json.loads(message.get("data"))
            logging.info(data)
        logging.debug(message)


def publish():
    redis_conn = redis.Redis(host=get_config('REDIS_HOST'), charset="utf-8", decode_responses=True)
    data = {
        "message": "hello",
    }
    redis_conn.publish(get_config('REDIS_CHANNEL'), json.dumps(data))
    logging.info(f"Message published to {get_config('REDIS_CHANNEL')}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")
    publish()
    main()
