from bluepy.sensortag import SensorTag


class Reader:

    def connect(self):
        pass

    def enable(self):
        pass

    def read(self):
        pass


class SensortagReader(Reader):

    def __init__(self, addr, extracted_sensor_types):

        self.addr = addr
        self.sensor_types = extracted_sensor_types
        self.tag = None
        self.sensors_fun = None

    def connect(self):
        self.tag = SensorTag(self.addr)
        self.sensors_fun = self.sensors_functions()

    def sensors_functions(self):
        return [getattr(self.tag, sensor) for sensor in self.sensor_types]

    def enable(self):
        for sensor_fun in self.sensors_fun:
            sensor_fun.enable()

    def read(self):
        measurement = dict()
        for sensor, sensor_fun in zip(self.sensor_types, self.sensors_fun):
            measurement[sensor] = sensor_fun.read()
        return measurement


SELECTED_READER = SensortagReader


def build_reader(addr, extracted_sensor_types):
    reader = SELECTED_READER(addr=addr, extracted_sensor_types=extracted_sensor_types)
    return reader
