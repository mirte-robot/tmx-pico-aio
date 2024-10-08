"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 DHT support courtesy of Martyn Wheeler
 Based on the DHTNew library - https://github.com/RobTillaart/DHTNew
"""

import asyncio
import sys

from tmx_pico_aio import tmx_pico_aio

"""
Setup a pin for digital output 
and toggle the pin 5 times.
"""

# some globals
DIGITAL_PIN = 18  # the board LED
pin2 = 19


async def blink(my_board, pin, pin2, pin3, pin4):
    # Set the DIGITAL_PIN as an output pin
    # set the pin mode
    await my_board.set_pin_mode_digital_output(pin)
    await my_board.set_pin_mode_digital_output(pin2)
    await my_board.set_pin_mode_digital_output(pin3)
    await my_board.set_pin_mode_digital_output(pin4)

    # toggle the pin 4 times and exit
    await my_board.digital_write(pin, 1)
    await my_board.digital_write(pin2, 0)
    await asyncio.sleep(0.5)

    for x in range(100000):
        print("ON", x)
        await my_board.digital_write(pin, 1)
        await my_board.digital_write(pin2, 0)
        await my_board.digital_write(pin3, 1)
        await my_board.digital_write(pin4, 0)
        await asyncio.sleep(0.01)
        print("OFF")
        await my_board.digital_write(pin, 0)
        await my_board.digital_write(pin2, 1)
        await my_board.digital_write(pin3, 0)
        await my_board.digital_write(pin4, 1)
        await asyncio.sleep(0.01)


# get the event loop
loop = asyncio.get_event_loop()
try:
    board = tmx_pico_aio.TmxPicoAio()
except KeyboardInterrupt:
    sys.exit()

try:
    # start the main function
    loop.run_until_complete(blink(board, DIGITAL_PIN, pin2, 20, 21))
    loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError:
    sys.exit(0)
