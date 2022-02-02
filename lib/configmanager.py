import sys
import os
import configparser


class ConfigManager:
    def __init__(self, configpath):
        self.configpath = configpath

        if not os.path.isfile(self.configpath):
            print(f"No such file or directory: {self.configpath}")
            sys.exit(1)

        self.parser = configparser.ConfigParser()

        try:
            self.parser.read(self.configpath)
        except configparser.Error as e:
            print(f"Failed to read config: {e}")
            sys.exit(2)

    # accessors
    def timeformat(self):
        return self.parser.get('application:units', 'timeformat')

    def dateformat(self):
        return self.parser.get('application:units', 'dateformat')

    def temperatureunit(self):
        return self.parser.get('application:units', 'temperatureunit')

    def pressureunit(self):
        return self.parser.get('application:units', 'pressureunit')
