import os
import psutil
import time

from lib.collectors.collector import GenericCollector


class SysStatsCollector(GenericCollector):
    def __init__(self):
        super().__init__('sys')
        self._setup()

    def _setup(self):
        pass

    def _collect(self):
        self.logger.debug(f"collector started")
        while self._readystate:
            load1, load5, load15 = psutil.getloadavg()
            cpu_usage = str((load15/os.cpu_count()) * 100) + "%"
            self.data = {
                "cpu": {
                    "usage": cpu_usage,
                    "load1": load1,
                    "load5": load5,
                    "load15": load15
                },
                "mem": {
                    "usage": psutil.virtual_memory()[2]
                }
            }
            time.sleep(0.5)
        self.logger.debug("readystate changed to false")

