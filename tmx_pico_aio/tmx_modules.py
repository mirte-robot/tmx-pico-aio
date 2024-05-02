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
            PrivateConstants.MODULE_TYPES.PCA9685,
            [
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
        self,
        uart_port,
        rx_pin,
        tx_pin,
        servo_ids=[],
        callback=None,
        callback_id_verify=None,
        callback_servo_range=None,
        callback_servo_offset=None,
    ):
        async def decode_callback(data):
            it_size = 3
            out = []
            message_type = data[0]
            if message_type == 0:
                data = data[1:]
                for i in range(0, len(data), 3):
                    id = servo_ids[data[i]]
                    angle = struct.unpack(">H", bytes([data[i + 1], data[i + 2]]))[0]
                    out.append({"id": id, "angle": angle})
                if callback != None:
                    await callback(out)
            elif message_type == 4:
                if callback_id_verify != None:
                    await callback_id_verify(data[1], data[2])
            elif message_type == 6:
                if callback_servo_range != None:
                    id = servo_ids[data[1]]
                    ranges = struct.unpack(">2H", bytes(data[2:]))
                    print(id, ranges)
                    await callback_servo_range(id, ranges)
            elif message_type == 8:
                if callback_servo_offset != None:
                    id = servo_ids[data[1]]
                    offset = struct.unpack(">h", bytes(data[2:]))[0]
                    await callback_servo_offset(id, offset)

        sensor_num = await self.add_module(
            PrivateConstants.MODULE_TYPES.HIWONDERSERVO,
            [
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

        async def verify_id(check_id):
            try:
                await self.send_module(sensor_num, [4, check_id])
            except ValueError as e:
                print(e)

        async def save_range(servo_id, min_r, max_r):
            try:
                id = servo_ids.index(servo_id)
                data_item = struct.pack(
                    ">2H",
                    min_r,
                    max_r,
                )
                await self.send_module(sensor_num, [5, id, *data_item])
            except Exception as e:
                print("err", e)
        async def save_voltage_range(servo_id, min_v, max_v):
            min_v = int(min_v*1000) # convert to mV
            max_v =int(max_v*1000)

            try:
                id = servo_ids.index(servo_id)
                data_item = struct.pack(
                    ">2H",
                    min_v,
                    max_v,
                )
                await self.send_module(sensor_num, [9, id, *data_item])
            except Exception as e:
                print("err", e)
        async def save_offset(servo_id, offset):
            try:
                id = servo_ids.index(servo_id)
                data_item = struct.pack(
                    ">h",
                    offset,
                )
                await self.send_module(sensor_num, [7, id, *data_item])
            except Exception as e:
                print("err", offset, e)

        async def get_range(servo_id):
            try:
                id = servo_ids.index(servo_id)
                await self.send_module(sensor_num, [6, id])
            except Exception as e:
                print(e)

        async def get_offset(servo_id):
            try:
                id = servo_ids.index(servo_id)
                await self.send_module(sensor_num, [8, id])
            except Exception as e:
                print(e)

        return {
            "set_single_servo": set_single_servo,
            "set_multiple_servos": set_multiple_servos,
            "set_enabled": set_enabled,
            "set_enabled_all": set_enabled_all,
            "set_id": set_id,
            "verify_id": verify_id,
            "save_range": save_range,
            "get_range": get_range,
            "save_offset": save_offset,
            "get_offset": get_offset,
            "save_voltage_range": save_voltage_range,
        }

    async def add_shutdown_relay(self, pin, pin_value, time):
        if time > 200 or time < 10:
            time = 20
        module_num = await self.add_module(
            PrivateConstants.MODULE_TYPES.SHUTDOWN_RELAY,
            [
                pin,
                int(pin_value),
                time,
            ],
            None,
        )

        async def trigger_shutdown_relay(enable=True):
            await self.send_module(module_num, [int(enable)])

        return trigger_shutdown_relay

    async def add_module(self, module_type, module_settings, callback):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_NEW, self.num, module_type.value, *module_settings]
        )
        self.callbacks.append(callback)
        self.num += 1

        return self.num - 1

    async def _module_reporter(self, report):
        cb = self.callbacks[report[0]]
        if cb != None:
            await cb(report[2:])

    async def send_module(self, module_num, data):
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_DATA, module_num, *data]
        )
