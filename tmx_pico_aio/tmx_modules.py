from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio
import struct

class TmxModules:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._module_reporter = self._module_reporter
        self.num = 0
        self.callbacks = []

    async def add_pca9685(self, i2c_port, callback=None):
        sensor_num = await self.add_module([PrivateConstants.MODULE_TYPES.PCA9685.value, i2c_port], callback)
        async def set_pwm(num, high, low=0):
            data = struct.pack('<2H', high, low)
            await self.send_module(sensor_num,[num, *data])
        return set_pwm
    
    async def add_module(self, module_settings, callback):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_NEW, self.num, *module_settings]
        )
        self.callbacks.append(callback)
        self.num += 1
        return self.num-1

    async def _module_reporter(self, report):
        await self.callbacks[report[0]](report[2:])
    async def send_module(self, module_num, data):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_DATA, module_num, *data]
        )