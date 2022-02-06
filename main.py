import sys
import logging
import json
import queue


from lib.sensors import Sensors
from lib.configmanager import ConfigManager
from lib.connection import Connection


class SensorD:
    def __init__(self, config_file):
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = ConfigManager(self.config_file)

        self.send_q = queue.Queue(maxsize=10)

        self.bind_addr = self.config.parser.get("application:listen_settings", "bind_addr")
        self.bind_port = self.config.parser.get("application:listen_settings", "bind_port")

        self.sensors = Sensors(self.config, self.send_q)
        self.connection = Connection(self.bind_addr, self.bind_port, self.sensors)

    def start(self):
        self.sensors.start()
        self.connection.start()

       # self.connection.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s")
    sensord = SensorD(sys.argv[1])
    sensord.start()
