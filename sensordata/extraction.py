import argparse
import logging
import time
import os
from multiprocessing import Process

from sensordata.extraction_fsm import finite_state_machine
from sensordata.util import ZMQParentSubscriber
from sensordata.writer import build_writers


def arguments_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device-addrs', required=True)
    parser.add_argument('--file_path', default="sensordata.json")
    parser.add_argument('-e', '--extracted-sensor-types', default="accelerometer,gyroscope,magnetometer,barometer")
    parser.add_argument('--publishing-host', default="*")
    parser.add_argument('--publishing-port', default="5557")
    parser.add_argument('--publishing-topic', default="sensor-data")
    parser.add_argument('-w', '--write-modes', default="shell,zmq,file")
    parser.add_argument('--without-filename-completion', action="store_true", default=False)
    parser.add_argument('--child-publishing-host', default="127.0.0.1")
    parser.add_argument('--child-publishing-port', default="5556")
    parser.add_argument('--child-publishing-topic', default="child-writer")
    parser.add_argument('-l', '--log', default=None)
    parser.add_argument('--log-level', default="INFO")
    parser.add_argument('--log-dir', default=".")
    return parser


def main():

    parser = arguments_parser()
    args = parser.parse_args()

    # Log Conf
    logging_level = getattr(logging, args.log_level.upper())
    log_dir = args.log_dir
    log_filename = args.log

    log_conf = {
        "level": logging_level
    }
    if log_filename is None:
        log_filename = "sensors-values-extraction-%s.log" % str(time.time())
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    log_path = os.path.join(log_dir, log_filename)
    log_conf.update({"filename": log_path})
    logging.basicConfig(**log_conf)

    fsm_args = vars(args)

    zmq_parent_subscriber = ZMQParentSubscriber(
        subscription_host=fsm_args["child_publishing_host"],
        subscription_topic=fsm_args["child_publishing_topic"],
        subscription_port=fsm_args["child_publishing_port"],
    )

    try:
        # Init one process per device
        fsm_processes = []
        for device_addr in [addr.strip() for addr in args.device_addrs.split(",")]:
            p_fsm_args = fsm_args.copy()
            p_fsm_args["device_addr"] = device_addr
            fsm_processes.append(Process(target=finite_state_machine, args=(p_fsm_args,)))

        # Start processes
        for fsm_process in fsm_processes:
            fsm_process.start()

        # Init writers
        sensor_writers = build_writers(**fsm_args)

        # Collect and write the watches' data
        while True:
            measurement_info_str = zmq_parent_subscriber.read()
            for sensor_writer in sensor_writers:
                sensor_writer.write(measurement_info_str)
    except KeyboardInterrupt as e:
        logging.warning("User KeyboardInterruption")
    finally:
        for fsm_process in fsm_processes:
            fsm_process.terminate()


if __name__ == '__main__':
    main()

