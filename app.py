from wakeonlan import send_magic_packet  # https://pypi.org/project/wakeonlan/
import socket
import time
from configurator.utility import get_config
from kme import KMEMessage, KME
import logging


def process_message(message: KMEMessage):
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
    return KMEMessage(topic='')


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
    k_client = KME(bootstrap_servers=[get_config('KAFKA_BOOSTRAP_SERVER')])
    logging.info(f"Subscribing to {get_config('KAFKA_TOPIC')}")
    k_client.subscribe(get_config('KAFKA_TOPIC'), consumer_group='me', callback=process_message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting")
    main()
