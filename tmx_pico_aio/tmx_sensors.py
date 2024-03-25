from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio
import struct


class TmxSensors:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._sensor_reporter = self._sensor_reporter
        self.num = 0
        self.callbacks = []

    async def add_adxl345(self, i2c_port, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.ADXL345, [i2c_port], callback
        )

    async def add_veml6040(self, i2c_port, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.VEML6040, [i2c_port], callback
        )

    async def add_vl53(self, i2c_port, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.TOF_VL53, [i2c_port], callback
        )

    async def add_mpu9250(self, i2c_port, callback):
        # data: 3 acc floats, 3 gyro floats, 3 mag floats, with float being 4 bytes
        async def mpu_callback(data):
            values = struct.unpack("f", bytes(data))
            acc = values[:3]
            gyro = values[3:6]
            mag = values[6:9]
            await callback(acc, gyro, mag)

        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.MPU_9250, [i2c_port], mpu_callback
        )

    async def add_hx711(self, out, sck, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.LOAD_CELL, [out, sck], callback
        )

    async def add_gps(self, rx, tx, uart_channel, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.GPS, [rx, tx, uart_channel], callback
        )

    async def add_ina226(self, i2c_port, callback, addr=0x40):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.INA226, [i2c_port, addr], callback
        )

    async def add_sensor(self, sensor_type, sensor_settings, callback):
        # print(sensor_settings)
        await self.pico_aio._send_command(
            [PrivateConstants.SENSOR_NEW, self.num, sensor_type.value, *sensor_settings]
        )
        self.callbacks.append(callback)
        self.num += 1

    async def _sensor_reporter(self, report):
        # print("sensor reporter")
        # print(report)
        await self.callbacks[report[0]](report[2:])
