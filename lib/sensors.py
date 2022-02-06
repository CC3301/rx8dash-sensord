import logging
import queue
import threading
import json
import time


from lib.collectors.hardwaresensorcollector import HardwareSensorCollector
from lib.collectors.canbuscollector import CANBusCollector
from lib.collectors.gpsdatacollector import GPSDataCollector
from lib.collectors.gyrocollector import GyroCollector
from lib.collectors.sysstatscollector import SysStatsCollector

from lib.sensordataprocessor import SensorDataProcessor


class Sensors:
    def __init__(self, config, send_q):
        self.config = config
        self.send_q = send_q
        self.logger = logging.getLogger(__name__)
        self.collectors = [CANBusCollector(), HardwareSensorCollector(), GPSDataCollector(), GyroCollector()]
        self.sdp = SensorDataProcessor(self.config)
        self.sensor_thread = threading.Thread(target=self.collect_and_process,
                                              name=self.__class__.__name__)
        self.__keep_running = False

        self.previous_result = None
        self.current_result = None
        self.data = None

    def start(self):
        self.__keep_running = True
        self.logger.debug("Starting collectors")
        for i, collector in enumerate(self.collectors):
            collector.start(i)
            while not collector.ready():
                pass
        self.logger.debug("all collectors available, starting aggregator thread")
        self.sensor_thread.start()

    def stop(self):
        self.__keep_running = False
        self.sensor_thread.join()
        self.logger.debug("stopped SensorAggregator, waiting for collectors to exit")
        for collector in self.collectors:
            collector.stop()
            collector.t.join()
        self.logger.debug("SensorAggregator has exited")

    def fetch(self):
        if self.previous_result != self.current_result:
            self.previous_result = self.current_result
            return self.data
        else:
            return None

    def collect_and_process(self):
        self.logger.debug("SensorAggregator started")
        while self.__keep_running:
            result = {}
            for collector in self.collectors:
                result[str(collector.result_prefix)] = collector.fetch()

            self.current_result = self.sdp.process(result)
            self.data = json.dumps(self.current_result).encode('utf-8')
