import logging

import time
from bluepy.btle import BTLEException
from sensordata.reader import build_reader
from sensordata.util import ZMQChildPublisher, stringify_measurement_info


# State Machine IDs
INIT = 1
CONNECT = 2
DISCONNECTED = 3
WAIT_RECONNECT = 4
COLLECTING = 5
END = 6
ERROR = 7


def init(state):
    logging.info("[%s] Initialisation Started" % state["device_addr"])
    init_sensor_reader(state)
    init_zmq_publisher(state)
    logging.info("[%s] Initialisation Finished" % state["device_addr"])
    return CONNECT


def init_sensor_reader(state):
    state["sensor_reader"] = build_reader(
        addr=state["device_addr"],
        extracted_sensor_types=state["extracted_sensor_types"]
    )
    logging.info("[%s] Reader Initialised" % state["device_addr"])


def init_zmq_publisher(state):

    zmq_publisher = ZMQChildPublisher(
        publishing_host=state["publishing_host"],
        publishing_port=state["publishing_port"],
        publishing_topic=state["publishing_topic"]
    )
    state["zmq_publisher"] = zmq_publisher
    logging.info("[%s] Publisher Initialised" % state["device_addr"])


def connect(state):

    next_fsm = None

    try:
        state["sensor_reader"].connect()
        state["sensor_reader"].enable()
        logging.info("[%s] Connection Established" % state["device_addr"])
        logging.info("[%s] Data Collecting Started" % state["device_addr"])
        next_fsm = COLLECTING

    except BTLEException as e:
        if e.code == e.DISCONNECTED:
            logging.warning("[%s] Unable to Connect" % state["device_addr"])
            next_fsm = DISCONNECTED
        else:
            logging.error(e)
            next_fsm = ERROR

    except BrokenPipeError:
        logging.warning("[%s] Broken Pipe" % state["device_addr"])
        next_fsm = DISCONNECTED

    except Exception as e:
        logging.exception(e)
        next_fsm = ERROR

    if next_fsm is None:
        logging.error("[%s] An unexpected behavior happened" % state["device_addr"])
        next_fsm = ERROR

    return next_fsm


def disconnected(state):
    logging.warning("[%s] Disconnected" % state["device_addr"])
    return WAIT_RECONNECT


def wait_reconnect(state):
    logging.info("[%s] Wait to Reconnect" % state["device_addr"])
    time.sleep(1)
    return CONNECT


def collecting(state):

    next_fsm = None

    try:
        measurement = state["sensor_reader"].read()
        measurement_info_str = stringify_measurement_info(
            addr=state["device_addr"],
            measurement=measurement
        )

        state["zmq_publisher"].write(measurement_info_str)
        next_fsm = COLLECTING

    except BTLEException as e:
        if e.code == e.DISCONNECTED:
            next_fsm = DISCONNECTED
        else:
            next_fsm = ERROR

    except BrokenPipeError:
        logging.warning("[%s] Broken Pipe" % state["device_addr"])
        next_fsm = DISCONNECTED

    except Exception as e:
        logging.exception(e)
        next_fsm = ERROR

    if next_fsm is None:
        logging.error("[%s] An unexpected behavior happened" % state["device_addr"])
        next_fsm = ERROR

    return next_fsm


def finite_state_machine(args):

    fsm = INIT
    state = {
        "extracted_sensor_types": [st.strip().lower() for st in args["extracted_sensor_types"].split(",")],
        "publishing_host": args["child_publishing_host"],
        "publishing_port": args["child_publishing_port"],
        "publishing_topic": args["child_publishing_topic"],
        "device_addr": args["device_addr"]
    }

    fsm_callbacks = {
        INIT: init,
        CONNECT: connect,
        DISCONNECTED: disconnected,
        WAIT_RECONNECT: wait_reconnect,
        COLLECTING: collecting
    }

    while fsm not in [END, ERROR]:

        current_fsm_callback = fsm_callbacks.get(fsm, None)
        if current_fsm_callback:
            fsm = current_fsm_callback(state)
        else:
            fsm = ERROR

    if fsm == END:
        logging.info("[%s] End" % state["device_addr"])
