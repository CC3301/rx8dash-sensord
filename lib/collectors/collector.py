import logging
import threading
import time


class GenericCollector:
    def __init__(self, result_prefix):
        self.data = {}
        self.result_prefix = result_prefix
        self._readystate = False

        self.logger = logging.getLogger(f'{__name__}({self.result_prefix})')
        self.t = threading.Thread(target=self._collect)

    def fetch(self):
        if not self._readystate:
            return {}
        return self.data

    def stop(self):
        self._readystate = False

    def ready(self):
        return self._readystate

    def start(self, i):
        self._readystate = True
        self.t.name = f"{__class__.__name__}#{i}"
        self.t.start()

    def _collect(self):
        pass
