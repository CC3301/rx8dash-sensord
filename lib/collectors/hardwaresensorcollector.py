import time

from lib.collectors.collector import GenericCollector


class HardwareSensorCollector(GenericCollector):
    def __init__(self):
        super().__init__('sen')
        self._setup()

    def _setup(self):
        pass

    def _collect(self):
        self.logger.debug(f"collector started")
        iterator = 0
        modifier = 1
        while self._readystate:
            self.data = {
                'oil': {
                    'temp': iterator + 273,  # temp offset
                    'pressure': iterator * 2 + 200
                },
                'water': {
                    'temp': iterator + 273  # temp offset
                }
            }
            iterator += modifier
            if iterator > 120:
                modifier = -1
            if iterator < 1:
                modifier = 1
            time.sleep(0.1)
        self.logger.debug("readystate changed to false")
