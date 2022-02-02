import logging
from datetime import datetime


class SensorDataProcessor:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config

        self._min_gauge_angle = 0
        self._max_gauge_angle = 290

        self._amb_temperature = 0
        self._engine_rpm = 0
        self._engine_tps = 0
        self._vehicle_velocity = 0
        self._vehicle_velocity_gps = 0

        self.gpstime = 0
        self.gpsdate = 0

        self.engine_oil_temperature = 0
        self.engine_oil_temperature_needle_position = 0
        self.engine_oil_temperature_status = "normal"

        self.engine_oil_pressure = 0
        self.engine_oil_pressure_needle_position = 0
        self.engine_oil_pressure_status = "normal"

        self.engine_water_temperature = 0
        self.engine_water_temperature_needle_position = 0
        self.engine_water_temperature_status = "normal"

        self.accel_x = 0
        self.accel_y = 0
        self.accel_z = 0

        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0

        self.temperature_symbol = self.config.parser.get('application:units', 'temperaturesymbol')
        self.pressure_symbol = self.config.parser.get('application:units', 'pressuresymbol')

        self.scale_factor_accel = self.pressure_symbol = self.config.parser.get('application:gyr:factors',
                                                                                'scale_factor_accel')
        self.scale_factor_gyro = self.pressure_symbol = self.config.parser.get('application:gyr:factors',
                                                                               'scale_factor_gyro')

        self.logger.debug("Sensor data processor initialized")

    @staticmethod
    def __convert_celsius(val):
        """
        :param val: temperature in kelvin
        :return: val converted to celsius
        """
        return int(val - 273.15)

    @staticmethod
    def __convert_fahrenheit(val):
        """
        :param val: temperature in kelvin
        :return: val converted to fahrenheit
        """
        return int(val * 9 / 5 - 459.67)

    @staticmethod
    def __convert_bar(val):
        """
        :param val: pressure in kpa
        :return: val converted to bar
        """
        return int(val / 100)

    @staticmethod
    def __scale(val, src, dst):
        """
        :param val: value
        :param src: source range, e.g. 0 - 100
        :param dst: destination range, e.g. 555 - 888
        :return: val corrected to be proportional to the destination range
        """
        return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

    # process current dataset
    def process(self, data):
        """
        :param data:
        :return:
        """

        # extract human-readable formats from the units returned by the sensor aggregator
        self.gpstime = datetime.fromtimestamp(data['gps']['time']).strftime(self.config.timeformat())
        self.gpsdate = datetime.fromtimestamp(data['gps']['time']).strftime(self.config.dateformat())

        # calculate gauges
        self._calculate_engine_oil_pressure(data['sen']['oil']['pressure'])
        self._calculate_engine_oil_temperature(data['sen']['oil']['temp'])
        self._calculate_engine_water_temperature(data['sen']['water']['temp'])

        # get gyro and accelerometer data
        self.accel_x = self._calculate_acceleration(data['gyr']['acc']['x'])
        self.accel_y = self._calculate_acceleration(data['gyr']['acc']['y'])
        self.accel_z = self._calculate_acceleration(data['gyr']['acc']['z'])

        self.gyro_x = self._calculate_gyro(data['gyr']['gyro']['x'])
        self.gyro_y = self._calculate_gyro(data['gyr']['gyro']['y'])
        self.gyro_z = self._calculate_gyro(data['gyr']['gyro']['z'])

        result = {
            "sen": {
                "oil": {
                    "pressure": {
                        "raw": data['sen']['oil']['pressure'],
                        "val": self.engine_oil_pressure,
                        "status": self.engine_oil_pressure_status,
                        "needle_rotation": self.engine_oil_pressure_needle_position
                    },
                    "temperature": {
                        "raw": data['sen']['oil']['temp'],
                        "val": self.engine_oil_temperature,
                        "status": self.engine_oil_temperature_status,
                        "needle_rotation": self.engine_oil_temperature_needle_position
                    }
                },
                "water": {
                    "temperature": {
                        "raw": data['sen']['water']['temp'],
                        "val": self.engine_water_temperature,
                        "status": self.engine_water_temperature_status,
                        "needle_rotation": self.engine_water_temperature_needle_position
                    }
                }
            },
            "can": {
                "engine": {
                    "rpm": {
                        "raw": data['can']['engine']['rpm']
                    },
                    "tps": {
                        "raw": data['can']['engine']['tps']
                    }
                },
                "vehicle": {
                    "velocity": {
                        "raw": data['can']['vehicle']['velocity']
                    }
                }
            },
            "gps": {
                "time": {
                    "raw": data['gps']['time'],
                    "time": self.gpstime,
                    "date": self.gpsdate
                }
            },
            "sys": {
                "cpu": {
                    "usage": data['sys']['cpu']['usage'],
                    "load1": data['sys']['cpu']['load1'],
                    "load5": data['sys']['cpu']['load5'],
                    "load15": data['sys']['cpu']['load15']
                },
                "mem": {
                    "usage": data['sys']['mem']['usage']
                }
            },
            "gyr": {
                "accel": {
                    "x": self.accel_x,
                    "y": self.accel_y,
                    "z": self.accel_z
                },
                "gyro": {
                    "x": self.gyro_x,
                    "y": self.gyro_y,
                    "z": self.gyro_z
                }
            }
        }

        return result

    def _calculate_acceleration(self, value):
        return value / self.scale_factor_accel

    def _calculate_gyro(self, value):
        return value / self.scale_factor_gyro

    def _calculate_gauge(self, value, max_value, min_value, high_value, low_value, gaugetype):
        """
        :param value: raw sensor value
        :param max_value: maximum value
        :param min_value: minimum value
        :param high_value: trigger for 'high' status i.e. warning lamp
        :param low_value: trigger for 'low' status i.e. "cold" lamp
        :return: gauge_status, needle_rotation, value_string
        """
        # range correction
        if value > max_value:
            value = max_value
        if value < min_value:
            value = min_value

        # which icon to show
        gauge_status = "normal"
        if value >= high_value:
            gauge_status = "high"
        if value <= low_value:
            gauge_status = "low"

        # needle rotation
        needle_rotation = self.__scale(value, (min_value, max_value), (self._min_gauge_angle, self._max_gauge_angle))

        # unit correction
        value_string = "invalid"
        if gaugetype == 'temp':
            if self.config.temperatureunit() == 'celsius':
                value = self.__convert_celsius(value)
            elif self.config.temperatureunit() == 'fahrenheit':
                value = self.__convert_fahrenheit(value)
            value_string = str(value) + " " + self.temperature_symbol
        elif gaugetype == 'pressure':
            if self.config.pressureunit() == 'bar':
                value = self.__convert_bar(value)
            value_string = str(value) + " " + self.pressure_symbol

        return gauge_status, needle_rotation, value_string

    def _calculate_engine_water_temperature(self, engine_water_temperature):
        """
        :param engine_water_temperature:
        :return:
        """
        max_value = int(self.config.parser.get("application:gauges:water_temperature", "max_value"))
        min_value = int(self.config.parser.get("application:gauges:water_temperature", "min_value"))

        high_value = int(self.config.parser.get("application:gauges:water_temperature", "high_value"))
        low_value = int(self.config.parser.get("application:gauges:water_temperature", "low_value"))

        self.engine_water_temperature_status, self.engine_water_temperature_needle_position, \
            self.engine_water_temperature = self._calculate_gauge(engine_water_temperature, max_value, min_value,
                                                                  high_value, low_value, 'temp')

    def _calculate_engine_oil_temperature(self, engine_oil_temperature):
        """
        :param engine_oil_temperature:
        :return:
        """
        max_value = int(self.config.parser.get("application:gauges:oil_temperature", "max_value"))
        min_value = int(self.config.parser.get("application:gauges:oil_temperature", "min_value"))

        high_value = int(self.config.parser.get("application:gauges:oil_temperature", "high_value"))
        low_value = int(self.config.parser.get("application:gauges:oil_temperature", "low_value"))

        self.engine_oil_temperature_status, self.engine_oil_temperature_needle_position, self.engine_oil_temperature = \
            self._calculate_gauge(engine_oil_temperature, max_value, min_value, high_value, low_value, 'temp')

    def _calculate_engine_oil_pressure(self, engine_oil_pressure):
        """
        :param engine_oil_pressure:
        :return:
        """
        max_value = int(self.config.parser.get("application:gauges:oil_pressure", "max_value"))
        min_value = int(self.config.parser.get("application:gauges:oil_pressure", "min_value"))

        high_value = int(self.config.parser.get("application:gauges:oil_pressure", "high_value"))
        low_value = int(self.config.parser.get("application:gauges:oil_pressure", "low_value"))

        self.engine_oil_pressure_status, self.engine_oil_pressure_needle_position, self.engine_oil_pressure = \
            self._calculate_gauge(engine_oil_pressure, max_value, min_value, high_value, low_value, 'pressure')
