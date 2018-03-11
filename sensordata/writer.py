import os
import zmq
import json


class Writer:
    def write(self, measurement_info_str):
        pass


class ShellWriter(Writer):

    def write(self, measurement_info_str):
        measurement_info = json.loads(measurement_info_str)
        print("{addr}\t{measurement}".format(**measurement_info))


class FileWriter(Writer):

    def __init__(self, file_path):
        self.file_path = file_path

    def write(self, measurement_info_str):
        with open(self.file_path, "a") as f:
            f.write(measurement_info_str + "\n")


class ZMQWriter(Writer):

    def __init__(self, publish_host, publish_port, publish_topic):
        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUB)
        self.zmq_socket.bind("tcp://%s:%s" % (publish_host, publish_port))
        self.zmq_publish_topic = publish_topic

    def write(self, measurement_info_str):
        topic_suffix = ""
        self.zmq_socket.send_string("%s%s %s" % (self.zmq_publish_topic, topic_suffix, measurement_info_str))


def build_writers(extracted_sensor_types, write_modes="shell", file_path=None, without_filename_completion=False,
                  publishing_host=None, publishing_port=None, publishing_topic=None,
                  **kwargs):

    sensor_writers = []
    write_modes = write_modes.lower()

    if "shell" in write_modes:
        sensor_writers.append(ShellWriter())

    if "file" in write_modes:

        filename, ext = os.path.basename(file_path).split(".")

        if not without_filename_completion:
            for v in extracted_sensor_types.split(","):
                filename += "-with-%s" % v

        file_path = os.path.join(os.path.dirname(file_path), filename + "." + ext)

        sensor_writers.append(FileWriter(file_path=file_path))

    if "zmq" in write_modes:
        sensor_writers.append(
            ZMQWriter(
                publish_host=publishing_host,
                publish_port=publishing_port,
                publish_topic=publishing_topic
            )
        )
    return sensor_writers