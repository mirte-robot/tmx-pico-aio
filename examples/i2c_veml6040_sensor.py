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

"""
This example sets up and control an ADXL345 i2c accelerometer.
It will continuously print data the raw xyz data from the device.
"""


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)  # compute negative value
    return val  # return positive value as is


# the call back function to print the adxl345 data
async def the_callback(data):
    # print(data, data[0]-data[2])
    R = (data[0] | data[1] << 8) / (255 * 255 / 100)
    G = (data[2] | data[3] << 8) / (255 * 255 / 100)
    B = (data[4] | data[5] << 8) / (255 * 255 / 100)
    W = (data[6] | data[7] << 8) / (255 * 255 / 100)
    print(f"R: {R:.2f} G: {G:.2f} B: {B:.2f} W: {W:.2f}")
    # print(f"x: {x:.2f} y: {y:.2f} z: {z:.2f}")


async def veml(my_board):
    await my_board.set_pin_mode_i2c(0, 4, 5)
    await asyncio.sleep(0.1)
    await my_board.sensors.add_veml6040(the_callback)
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
    loop.run_until_complete(veml(board))
    print("done veml")
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
