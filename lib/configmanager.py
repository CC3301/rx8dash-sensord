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
    def loggingformat(self):
        return self.parser.get('application:core', 'loggingformat')

    def loglevel(self):
        return self.parser.get('application:core', 'loglevel')

    def timeformat(self):
        return self.parser.get('application:units', 'timeformat')

    def dateformat(self):
        return self.parser.get('application:units', 'dateformat')

    def temperatureunit(self):
        return self.parser.get('application:units', 'temperatureunit')

    def pressureunit(self):
        return self.parser.get('application:units', 'pressureunit')

    def temperaturesymbol(self):
        return self.parser.get('application:units', 'temperaturesymbol')

    def pressuresymbol(self):
        return self.parser.get('application:units', 'pressuresymbol')

    def mainbackgroundcolor(self):
        return self.parser.get('application:gui', 'background')

    def mainfontcolor(self):
        return self.parser.get('application:gui', 'fontcolor')

    def windowwidth(self):
        return self.parser.get('hardware:screen', 'width')

    def windowheight(self):
        return self.parser.get('hardware:screen', 'height')
