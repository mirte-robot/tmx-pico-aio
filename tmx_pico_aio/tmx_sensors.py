from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio


class TmxSensors:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._sensor_reporter = self._sensor_reporter
        self.num = 0
        self.callbacks = []

    async def add_adxl345(self, callback): # TODO: i2c port
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.ADXL345.value, 0], callback)
    async def add_veml6040(self, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.VEML6040.value, 0], callback)
    async def add_vl53(self, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.TOF_VL53.value, 0], callback)
    async def add_mpu9250(self, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.MPU_9250.value, 0], callback)
    async def add_hx711(self,out, sck, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.LOAD_CELL.value,out, sck], callback)
    async def add_gps(self,rx,tx, uart_channel, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.GPS.value,rx,tx, uart_channel], callback)

    async def add_sensor(self, sensor_settings, callback):
        # print(sensor_settings)
        await self.pico_aio._send_command(
            [PrivateConstants.SENSOR_NEW, self.num, *sensor_settings]
        )
        self.callbacks.append(callback)
        self.num += 1

    def _sensor_reporter(self, report):
        # print("sensor reporter")
        print(report)
        self.callbacks[report[0]](report[2:])
        pass
