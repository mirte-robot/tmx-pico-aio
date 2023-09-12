from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio


class TmxSensors:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._sensor_reporter = self._sensor_reporter
        self.num = 0
        self.callbacks = []

    async def add_adxl345(self, callback):
        await self.add_sensor([PrivateConstants.SENSOR_TYPES.ADXL345.value, 0], callback)

    async def add_sensor(self, sensor_settings, callback):
        print(sensor_settings)
        await self.pico_aio._send_command(
            [PrivateConstants.SENSOR_NEW, self.num, *sensor_settings]
        )
        self.callbacks.append(callback)
        self.num += 1

    def _sensor_reporter(self, report):
        # print("sensor reporter")
        # print(report)
        self.callbacks[report[0]](report[2:])
        pass
