from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio
import struct


class TmxModules:
    def __init__(self, tmx_pico_aio: TmxPicoAio):
        self.pico_aio = tmx_pico_aio
        self.pico_aio._module_reporter = self._module_reporter
        self.num = 0
        self.callbacks = []

    async def add_pca9685(self, i2c_port, addr=0x40, frequency=200, callback=None):
        sensor_num = await self.add_module(
            [
                PrivateConstants.MODULE_TYPES.PCA9685.value,
                i2c_port,
                addr,
                *struct.pack(">H", frequency),
            ],
            callback,
        )

        async def set_multiple_pwm(datas):
            data = []
            for d in datas:
                data.append(d["pin"])
                data.extend(struct.pack("<2H", d["low"], d["high"]))
            await self.send_module(sensor_num, data)

        async def set_pwm(num, high, low=0):
            low = int(low)
            high = int(high)
            data = struct.pack("<2H", low, high)
            await self.send_module(sensor_num, [num, *data])

        return {"set_pwm": set_pwm, "set_multiple_pwm": set_multiple_pwm}

    async def add_hiwonder_servo(
        self, uart_port, rx_pin, tx_pin, servo_ids=[], callback=None
    ):
        async def decode_callback(data):
            it_size = 3
            out = []
            for i in range(0, len(data), 3):
                id = servo_ids[data[i]]
                angle = struct.unpack(">H", bytes([data[i + 1], data[i + 2]]))[0]
                out.append({"id": id, "angle": angle})
            await callback(out)

        sensor_num = await self.add_module(
            [
                PrivateConstants.MODULE_TYPES.HIWONDERSERVO.value,
                uart_port == 1,
                rx_pin,
                tx_pin,
                len(servo_ids),
            ]
            + servo_ids,
            decode_callback,
        )

        async def set_single_servo(servo_id, angle, time=100):
            try:
                id = servo_ids.index(servo_id)
                data = struct.pack(">2H", angle, time)
                await self.send_module(sensor_num, [1, 1, id, *data])
            except ValueError as e:
                print(e)

        # will send the commands to all and then update
        async def set_multiple_servos(id_angles):  # list of id, angle, time
            try:
                data = []
                for id_angle in id_angles:
                    id = servo_ids.index(id_angle["id"])
                    data_item = struct.pack(
                        ">2H",
                        id_angle["angle"],
                        id_angle["time"] if "time" in id_angle else 100,
                    )
                    data.append(id)
                    data.extend(data_item)

                await self.send_module(sensor_num, [1, len(id_angles), *data])
            except ValueError as e:
                print(e)

        async def set_enabled(id, enabled):
            try:
                id = servo_ids.index(id)
                await self.send_module(sensor_num, [2, 1, id, 1 if enabled else 0])
            except ValueError as e:
                print(e)

        async def set_enabled_all(enabled):
            try:
                await self.send_module(sensor_num, [2, 0, 1 if enabled else 0])
            except ValueError as e:
                print(e)

        async def set_id(new_id):
            # This will set the id of all the connected servos, so do it one by one
            try:
                await self.send_module(sensor_num, [3, new_id])
            except ValueError as e:
                print(e)

        return {
            "set_single_servo": set_single_servo,
            "set_multiple_servos": set_multiple_servos,
            "set_enabled": set_enabled,
            "set_enabled_all": set_enabled_all,
            "set_id": set_id,
        }

    async def add_shutdown_relay(self, pin, pin_value, time):
        if(time > 200 or time < 10):
            time = 20
        module_num = await self.add_module([PrivateConstants.MODULE_TYPES.SHUTDOWN_RELAY.value,
pin, int(pin_value), time], None)

        async def trigger_shutdown_relay(enable=True):
            await self.send_module(module_num, [int(enable)])
        return trigger_shutdown_relay


    async def add_module(self, module_settings, callback):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_NEW, self.num, *module_settings]
        )
        self.callbacks.append(callback)
        self.num += 1

        return self.num - 1

    async def _module_reporter(self, report):
        cb = self.callbacks[report[0]]
        if(cb != None):
            await cb(report[2:])

    async def send_module(self, module_num, data):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_DATA, module_num, *data]
        )
