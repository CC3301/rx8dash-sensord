import smbus
import time


from lib.collectors.collector import GenericCollector


class GyroCollector(GenericCollector):
    def __init__(self):
        super().__init__('gyr')
        self._setup()

    def _setup(self):
        self.PWR_MGMT_1 = 0x6B
        self.SMPLRT_DIV = 0x19
        self.CONFIG = 0x1A
        self.GYRO_CONFIG = 0x1B
        self.INT_ENABLE = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H = 0x43
        self.GYRO_YOUT_H = 0x45
        self.GYRO_ZOUT_H = 0x47

        self.device_addr = 0x68
        self.bus = smbus.SMBus(0)

        # write to sample rate register
        self.bus.write_byte_data(self.device_addr, self.SMPLRT_DIV, 7)

        # Write to power management register
        self.bus.write_byte_data(self.device_addr, self.PWR_MGMT_1, 1)

        # Write to Configuration register
        self.bus.write_byte_data(self.device_addr, self.CONFIG, 0)

        # Write to Gyro configuration register
        self.bus.write_byte_data(self.device_addr, self.GYRO_CONFIG, 24)

        # Write to interrupt enable register
        self.bus.write_byte_data(self.device_addr, self.INT_ENABLE, 1)

    def __read_raw_data(self, addr):
        high = self.bus.read_byte_data(self.device_addr, addr)
        low = self.bus.read_byte_data(self.device_addr, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if value > 32768:
            value = value - 65536
        return value

    def _collect(self):
        self.logger.debug(f"collector started")
        while self._readystate:
            # Read Accelerometer raw value
            acc_x = self.__read_raw_data(self.ACCEL_XOUT_H)
            acc_y = self.__read_raw_data(self.ACCEL_YOUT_H)
            acc_z = self.__read_raw_data(self.ACCEL_ZOUT_H)

            # Read Gyroscope raw value
            gyro_x = self.__read_raw_data(self.GYRO_XOUT_H)
            gyro_y = self.__read_raw_data(self.GYRO_YOUT_H)
            gyro_z = self.__read_raw_data(self.GYRO_ZOUT_H)

            self.data = {
                "acc": {
                    "x": acc_x,
                    "y": acc_y,
                    "z": acc_z
                },
                "gyro": {
                    "x": gyro_x,
                    "y": gyro_y,
                    "z": gyro_z
                }
            }
            time.sleep(0.5)
        self.logger.debug("readystate changed to false")
