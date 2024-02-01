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
import struct
from tmx_pico_aio import tmx_pico_aio

"""
This example sets up and control an ADXL345 i2c accelerometer.
It will continuously print data the raw xyz data from the device.
"""


# the call back function to print the 9250 data
async def the_callback(data):
    if len(data) != 9 * 4:
        print("wrong length")
        return
    ints = list(map(lambda i: i.to_bytes(1, "big"), data))
    bytes_obj = b"".join(ints)
    vals = list(struct.unpack("<9f", bytes_obj))
    print(
        f"x: {vals[0]: >8.2f} y: {vals[1]: >8.2f} z: {vals[2]: >8.2f} rx: {vals[3]: >8.2f} ry: {vals[4]: >8.2f} rz: {vals[5]: >8.2f} gx: {vals[6]: >8.2f} gy: {vals[7]: >8.2f} gz: {vals[8]: >8.2f}"
    )


async def mpu9250(my_board):
    i2c_port = 0
    scl = 5
    sda = 4
    await my_board.set_pin_mode_i2c(i2c_port, sda, scl)
    await asyncio.sleep(0.1)
    await my_board.sensors.add_mpu9250(i2c_port, the_callback)
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
    loop.run_until_complete(mpu9250(board))
    print("done mpu")
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
