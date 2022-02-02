import smbus


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

            # Full scale range +/- 250 degree/C as per sensitivity scale factor
            ax = acc_x / 16384.0
            ay = acc_y / 16384.0
            az = acc_z / 16384.0

            gx = gyro_x / 131.0
            gy = gyro_y / 131.0
            gz = gyro_z / 131.0

            self.data = {
                "a": {
                    "x": ax,
                    "y": ay,
                    "z": az
                },
                "g": {
                    "x": gx,
                    "y": gy,
                    "z": gz
                }
            }
        self.logger.debug("readystate changed to false")
