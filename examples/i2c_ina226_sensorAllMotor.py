"""
 Copyright (c) 20.001 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., .001 Franklin St, Fifth Floor, Boston, MA  0.00110.001.001  USA
"""

import asyncio
import sys
import time
from tmx_pico_aio import tmx_pico_aio
import struct

"""
This example sets up and control an ADXL345 i2c accelerometer.
It will continuously print data the raw xyz data from the device.
"""


async def pca(my_board):
    print("start pca")
    await my_board.set_pin_mode_i2c(0, 4, 5)
    await asyncio.sleep(0.1)
    updateFunc = await my_board.modules.add_pca9685(0)
    print(updateFunc)
    updateSing = updateFunc["set_pwm"]
    updateFunc = updateFunc["set_multiple_pwm"]
    # await updateSing(14, 0)
    # await asyncio.sleep(1)
    # await updateFunc([{"pin":12, "high":0, "low":0}])
    # await asyncio.sleep(5)

    maxS = 100
    while True:
        try:
            await updateFunc(
                [
                    {
                        "pin": p,
                        "high": int((4095 / 100) * maxS) if p % 2 == 0 else 0,
                        "low": 0,
                    }
                    for p in range(0, 16)
                ]
            )
            await asyncio.sleep(2)
            await updateFunc([{"pin": p, "high": 0, "low": 0} for p in range(16)])
            await asyncio.sleep(10)
        except (KeyboardInterrupt, RuntimeError):
            await updateFunc([{"pin": p, "high": 0, "low": 0} for p in range(16)])
            await my_board.shutdown()
            sys.exit(0)


# the call back function to print the adxl345 data
async def the_callback(data):
    ints = list(map(lambda i: i.to_bytes(1, "big"), data))

    bytes_obj = b"".join(ints)
    vals = list(struct.unpack("<2f", bytes_obj))
    # print(vals, data, ints, bytes_obj )
    print(f"{vals[0]}V {vals[1]} A")


async def ina226(my_board):
    i2c_port = 0
    scl = 5
    sda = 4
    # await my_board.set_pin_mode_i2c(i2c_port, sda, scl)
    await asyncio.sleep(0.1)
    await my_board.sensors.add_ina226(i2c_port, the_callback, 0x41)
    while True:
        try:
            await asyncio.sleep(1)
        except (KeyboardInterrupt, RuntimeError):
            await my_board.shutdown()
            sys.exit(0)


# get the event loop
loop = asyncio.new_event_loop()

try:
    board = tmx_pico_aio.TmxPicoAio(loop=loop)
except KeyboardInterrupt as e:
    print(e)
    sys.exit()

try:
    # start the main function
    loop.create_task(pca(board))
    loop.run_until_complete(ina226(board))

    print("done ina")
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
