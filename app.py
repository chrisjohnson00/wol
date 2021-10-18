from wakeonlan import send_magic_packet  # https://pypi.org/project/wakeonlan/
import socket
import time
from configurator.utility import get_config
import pygogo as gogo
import pulsar
from _pulsar import ConsumerType
from json import loads, dumps

# logging setup
kwargs = {}
formatter = gogo.formatters.structured_formatter
logger = gogo.Gogo('struct', low_formatter=formatter).get_logger(**kwargs)


def process_message(message):
    # message = { 'name': 'nfs2',
    #                     'mac_address': 'b8:ca:3a:5d:28:b8',
    #                     'ip': '192.168.1.132',
    #                     'port': '22',
    #                     'pulsar_completion_topic': 'some optional completion topic name'
    #                   }
    logger.info("Sending magic packet")
    message_body = message
    logger.debug(f"Sending broadcast to {message_body['mac_address']}")
    send_magic_packet(message_body['mac_address'])
    logger.info(f"Checking every 1m if {message_body['ip']}:{message_body['port']} is open")
    ready = is_open(message_body['ip'], message_body['port'])
    while not ready:
        logger.info(f"{message_body['ip']}:{message_body['port']} is not yet open, checking again in 60s")
        ready = is_open(message_body['ip'], message_body['port'])
        time.sleep(60)
    logger.info(f"{message_body['name']} is up and ready for business")
    return True


def is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:  # noqa: E722
        logger.exception(f"Unable to connect to {ip}:{port}")
        return False


def send_message(message, pulsar_topic):
    pulsar_server = get_config('PULSAR_SERVER')
    client = pulsar.Client(f"pulsar://{pulsar_server}")
    producer = client.create_producer(pulsar_topic)
    producer.send(dumps(message).encode('utf-8'))
    logger.info("Message sent", extra={'message_body': message, 'topic': pulsar_topic})
    client.close()


def main():
    client = pulsar.Client(f"pulsar://{get_config('PULSAR_SERVER')}")
    consumer = client.subscribe(get_config('PULSAR_TOPIC'), get_config('PULSAR_SUBSCRIPTION'),
                                consumer_type=ConsumerType.Shared)
    logger.info(f"Subscribing to {get_config('PULSAR_TOPIC')}")

    while True:
        msg = consumer.receive()
        try:
            # decode from bytes, encode with backslashes removed, decode back to a string, then load it as a dict
            message_body = loads(msg.data().decode().encode('latin1', 'backslashreplace').decode('unicode-escape'))
            woke = process_message(message_body)
            if 'pulsar_completion_topic' in message_body and woke:
                send_message(message_body, message_body['pulsar_completion_topic'])
            if woke:
                consumer.acknowledge(msg)
            else:
                consumer.negative_acknowledge(msg)
        except:  # noqa: E722
            # Message failed to be processed
            consumer.negative_acknowledge(msg)

    client.close()


if __name__ == '__main__':
    logger.info("Starting")
    main()
