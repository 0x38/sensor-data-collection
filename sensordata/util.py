import time
import json
import zmq


def stringify_measurement_info(addr, measurement):
    state = {
        "timestamp": time.time(),
        "addr": addr,
        "measurement": measurement
    }
    return json.dumps(state).replace(" ", "")


class ZMQChildPublisher:

    def __init__(self, publishing_host="127.0.0.1", publishing_port="5556", publishing_topic="child-writer"):

        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUB)
        self.zmq_socket.connect("tcp://%s:%s" % (publishing_host, publishing_port))
        self.zmq_publishing_topic = publishing_topic

    def write(self, measurement_info_str):
        self.zmq_socket.send_string("%s %s" % (self.zmq_publishing_topic, measurement_info_str))


class ZMQParentSubscriber:
    def __init__(self, subscription_host="127.0.0.1", subscription_topic="child-writer", subscription_port="5556"):
        context = zmq.Context()
        self.subscription_socket = context.socket(zmq.SUB)
        self.subscription_socket.setsockopt_string(zmq.SUBSCRIBE, subscription_topic)
        self.subscription_socket.bind('tcp://%s:%s' % (subscription_host, subscription_port))
        self.subscription_port = subscription_port
        self.subscription_topic = subscription_topic

    def read(self):
        raw_msg = self.subscription_socket.recv()
        topic, msg = raw_msg.split()
        return msg.decode()
