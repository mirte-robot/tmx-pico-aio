from tmx_pico_aio.private_constants import PrivateConstants
from tmx_pico_aio.tmx_pico_aio import TmxPicoAio
import struct
import time
import asyncio


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
            min_v = int(min_v * 1000)  # convert to mV
            max_v = int(max_v * 1000)

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

    async def add_tmx_ssd1306(self, i2c_port):
        width = 128
        height = 64

        events = [
            0 for n in range(0, 4)
        ]  # just 4 types of messages, making this function not reentrant
        events_data = [[0] for n in range(0, 4)]

        async def cb(x):
            print(x)
            try:
                oled_msg_type = x[0]
                events[oled_msg_type].set()
                events_data[oled_msg_type] = x
            except Exception as e:
                pass

        module_num = await self.add_module(
            PrivateConstants.MODULE_TYPES.TMX_SSD1306, [int(i2c_port)], cb
        )

        # easy enum
        TEXT = 0
        TEXT_WRITE = 1
        BINARY = 2
        BINARY_WRITE = 3

        async def send_text(text):
            text = text.encode("ascii", errors="ignore").decode()
            text = text[0:150]  # truncate to 150 chars
            text_arr = list(map(ord, text))
            max_len = 30 - 4
            text_arrs = [
                text_arr[i : i + max_len] for i in range(0, len(text_arr), max_len)
            ]
            event = asyncio.Event()
            events[TEXT_WRITE] = event
            for arr in text_arrs:
                await self.send_module(module_num, [TEXT, len(arr), *arr])
            await self.send_module(module_num, [TEXT_WRITE])

            # waiting for the acknowledge after writing to the real oled
            try:
                await asyncio.wait_for(
                    event.wait(), 5
                )  # wait 1 second for the acknowledgement message
            except Exception as e:
                print(e)
                print(event.is_set(), events[1])
                print("not acknowledged oled send_write")
                return False

            data = events_data[TEXT_WRITE]

            if (
                data[1] > 200
            ):  # signed -> unsigned number, str can be max 150, 255==error
                print("Write failed oled send_write")
                return False
            if data[1] != len(text):
                print("diff len str")
            return True

        async def send_image(image):
            if image.mode != "1":
                return False
            start = time.time()
            event = asyncio.Event()
            events[BINARY_WRITE] = event
            buffer = [0] * (width * height)
            imwidth, imheight = image.size
            if imwidth != width or imheight != height:
                raise ValueError(
                    "Image must be same dimensions as display ({0}x{1}).".format(
                        width, height
                    )
                )
            pix = image.load()
            index = 0
            buffer_flat = []
            for y in range(height):

                for x in range(width):
                    buffer_flat.append(pix[x, y])
            buffer_e = []
            for height_block in range(height // 8):
                for x in range(width):
                    byt = 0
                    for bit in range(8):
                        byt = byt << 1
                        byt |= (
                            1
                            if buffer_flat[
                                x + (7 - bit) * width + height_block * width * 8
                            ]
                            else 0
                        )
                    buffer_e.append(byt)
            max_len = 16
            buff_arrs = [
                buffer_e[i : i + max_len] for i in range(0, len(buffer_e), max_len)
            ]
            i = 0
            for arr in buff_arrs:
                await self.send_module(
                    module_num, [BINARY, i, *arr]
                )  # send BINARY, index and 16 bytes
                i += 1
            await self.send_module(module_num, [BINARY_WRITE])  # send binary done

            # waiting for the acknowledge after writing to the real oled
            try:
                await asyncio.wait_for(
                    event.wait(), 1
                )  # wait 1 second for the acknowledgement message
            except Exception as e:
                print(e)
                print(event.is_set(), events[BINARY_WRITE])
                print("not acknowledged oled send_write img")
                return False

            data = events_data[BINARY_WRITE]

            if data[1] > 200:  # 255==error
                print("Write failed oled send_write img")
                return False
            if data[1] != 1:
                print("err ack")
            return True

        return {"send_text": send_text, "send_image": send_image}

    async def add_module(self, module_type, module_settings, callback):
        print(module_settings)
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
        # print(data, len(data))
        await self.pico_aio._send_command(
            [PrivateConstants.MODULE_DATA, module_num, *data]
        )
