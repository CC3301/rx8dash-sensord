import logging
import threading

from lib.collectors.hardwaresensorcollector import HardwareSensorCollector
from lib.collectors.canbuscollector import CANBusCollector
from lib.collectors.gpsdatacollector import GPSDataCollector

from lib.sensordataprocessor import SensorDataProcessor


class Sensors:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.collectors = [CANBusCollector(), HardwareSensorCollector(), GPSDataCollector()]
        self.sdp = SensorDataProcessor(self.config)
        self.sensor_thread = threading.Thread(target=self.collect_and_process,
                                              name=self.__class__.__name__)
        self.__keep_running = False

        self.previous_result = {}
        self.result = {}

    def start(self):
        self.__keep_running = True
        for i, collector in enumerate(self.collectors):
            collector.start(i)
        self.sensor_thread.start()

    def stop(self):
        self.__keep_running = False
        self.sensor_thread.join()

    def fetch(self):
        return self.result

    def collect_and_process(self):
        while self.__keep_running:
            result = {}
            for collector in self.collectors:
                result[str(collector.result_prefix)] = collector.fetch()

            if result != self.previous_result:
                self.previous_result = result
                self.result = self.sdp.process(result)
