import sys
import logging
from queue import Queue

from lib.sensors import Sensors
from lib.configmanager import ConfigManager


class SensorD:
    def __init__(self, config_file):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.queue = Queue()
        self.config = ConfigManager(self.config_file)

        self.sensors = Sensors(self.config)
        # self.connhandler = ConnectionHandler(self.queue)

    def start(self):
        self.sensors.start()
        while True:
            print(self.sensors.fetch())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
    sensord = SensorD(sys.argv[1])
    sensord.start()
