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

    x = twos_comp(data[1] << 8 | data[0], 16)*0.004
    y = twos_comp(data[3] << 8 | data[2], 16)*0.004
    z = twos_comp(data[5] << 8 | data[4], 16)*0.004

    print(f"x: {x} y: {y} z: {z}")
    print()


async def adxl345(my_board):
    # setup adxl345
    # device address = 83
    await my_board.set_pin_mode_i2c(0, 4, 5)
    await asyncio.sleep(0.1)

    # set up power and control register
    await my_board.i2c_write(83, [45, 0])
    await asyncio.sleep(0.001)
    await my_board.i2c_write(83, [45, 8])
    await asyncio.sleep(0.001)
    # set up the data format register
    await my_board.i2c_write(83, [49, 8])  # 0b0000_1000 = FULL_RES, +- 2g
    await asyncio.sleep(0.001)
    # await my_board.i2c_write(83, [49, 3]) # why set the same register?
    # await asyncio.sleep(.001)
    while True:
        # read 6 bytes from the data register
        try:
            out = await my_board.i2c_read(83, 50, 6) # takes 2ms
            if(not out):
                print("failed read")
                await my_board.shutdown()
                sys.exit(0)
            the_callback(out[5:])
            await asyncio.sleep(0.001)
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
    loop.run_until_complete(adxl345(board))
    print("done axl")
    # loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
