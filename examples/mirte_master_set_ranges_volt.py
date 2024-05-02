"""
 Copyright (c) 2024 Arend-Jan van Hilten

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
"""

import asyncio
import sys
import time

from tmx_pico_aio import tmx_pico_aio


ids = [2, 3, 4, 5, 6]

# TODO
ranges = {
    2: {"min": 3400, "max": 21000, "home": 12000},
    3: {"min": 2832, "max": 20000, "home": 11450},
    4: {"min": 120, "max": 21000, "home": 11750},
    5: {"min": 1128, "max": 21672, "home": 12200},
    6: {"min": 6168, "max": 14224, "home": 10524},
}


async def callback(data):
    pass


async def callback_servo_range(id, range):
    pass


async def update_one(the_board, id):
    updaters = await the_board.modules.add_hiwonder_servo(
        0, 0, 1, [id], callback, callback_servo_range=callback_servo_range
    )

    if id in ranges:
        await updaters["save_range"](id, ranges[id]["min"], ranges[id]["max"])
        await updaters["save_offset"](id, 0)
        await asyncio.sleep(0.1)
        await updaters["set_single_servo"](id, ranges[id]["home"], 1000)
        await asyncio.sleep(0.1)
        await updaters["save_voltage_range"](id, 10.5,14)
        await asyncio.sleep(1)


async def save_ranges(the_board):
    for x in range(2, 7):
        print(x)
        await update_one(the_board, x)


# get the event loop
loop = asyncio.get_event_loop()
try:
    board = tmx_pico_aio.TmxPicoAio()
except KeyboardInterrupt:
    sys.exit()

try:
    # start the main function
    loop.run_until_complete(save_ranges(board))
    # loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    # print("final range:", ranges)
    # loop.run_until_complete(save_ranges())
    # loop.run_until_complete(board.shutdown())
    sys.exit(0)
