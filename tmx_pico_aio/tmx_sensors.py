from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio


class TmxSensors:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._sensor_reporter = self._sensor_reporter
        self.num = 0
        self.callbacks = []

    def __getattribute__(self, name):
        if name.startswith("add_"):
            print("Sensor not supported in this version.")
        return None

    async def add_veml6040(self, i2c_port, callback):
        await self.add_sensor(
            PrivateConstants.SENSOR_TYPES.VEML6040, [i2c_port], callback
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
