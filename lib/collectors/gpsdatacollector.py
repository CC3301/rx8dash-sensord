import random
import time

from lib.collectors.collector import GenericCollector


class GPSDataCollector(GenericCollector):
    def __init__(self):
        super().__init__('gps')
        self._setup()

    def _setup(self):
        pass

    def _collect(self):
        self.logger.debug(f"collector started")
        while self._readystate:
            i = random.randint(0, 100)
            self.data = {
                'position': {
                    'lat': i,
                    'long': i,
                    'height': i
                },
                'attributes': {
                    'speed': i
                },
                'time': time.time()
            }
            time.sleep(0.5)
        self.logger.debug("readystate changed to false")

