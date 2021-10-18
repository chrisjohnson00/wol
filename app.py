from wakeonlan import send_magic_packet  # https://pypi.org/project/wakeonlan/
import socket
import time
from configurator.utility import get_config
import logging
import pulsar
from json import loads, dumps


def process_message(message):
    # message = { 'name': 'nfs2',
    #                     'mac_address': 'b8:ca:3a:5d:28:b8',
    #                     'ip': '192.168.1.132',
    #                     'port': '22'
    #                   }
    logging.info("Sending magic packet")
    message_body = message
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
    except:  # noqa: E722
        logging.exception(f"Unable to connect to {ip}:{port}")
        return False


def main():
    client = pulsar.Client(f"pulsar://{get_config('PULSAR_SERVER')}")
    consumer = client.subscribe(get_config('PULSAR_TOPIC'), get_config('PULSAR_SUBSCRIPTION'))
    logging.info(f"Subscribing to {get_config('PULSAR_TOPIC')}")

    while True:
        msg = consumer.receive()
        try:
            # decode from bytes, encode with backslashes removed, decode back to a string, then load it as a dict
            message_body = loads(msg.data().decode().encode('latin1', 'backslashreplace').decode('unicode-escape'))
            process_message(message_body)
            consumer.acknowledge(msg)
        except:  # noqa: E722
            # Message failed to be processed
            consumer.negative_acknowledge(msg)

    client.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")
    main()
