import time
import logging

from lib.collectors.hardwaresensorcollector import HardwareSensorCollector
from lib.collectors.canbuscollector import CANBusCollector
from lib.collectors.gpsdatacollector import GPSDataCollector


class SensorAggregator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.__keep_running = False
        self.previous_result = {}

        self.collectors = [CANBusCollector(), HardwareSensorCollector(), GPSDataCollector()]

    def fetch(self):
        return self.previous_result

    def start(self):
        self.logger.debug("Starting collectors")
        self.__keep_running = True
        for i, collector in enumerate(self.collectors):
            collector.start(i)
            while not collector.ready():
                pass
        self.logger.debug("all collectors available, starting aggregator thread")

    def ready(self):
        return self.__keep_running

    def stop(self):
        self.__keep_running = False
        self.logger.debug("stopped SensorAggregator, waiting for collectors to exit")
        for collector in self.collectors:
            collector.stop()
            collector.t.join()
        self.logger.debug("SensorAggregator has exited")

    def collect_and_aggregate(self):
        self.logger.debug("SensorAggregator started")
        while self.__keep_running:
            result = {}
            for collector in self.collectors:
                result[str(collector.result_prefix)] = collector.fetch()

            if result != self.previous_result:
                self.previous_result = result

            # it will take some time until the collectors have collected new data (CAN speed, sensor value
            # interpretation)
            time.sleep(0.1)
        self.logger.debug("readystate changed to false")
