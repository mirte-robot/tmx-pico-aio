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
import aioconsole

from tmx_pico_aio import tmx_pico_aio


ids = [2,3,4,5,6]

# TODO
ranges = {
    2: {"min": 0, "max": 24000, "home": 20000, "offset": 0},
    3: {"min": 0, "max": 24000, "home": 20000, "offset": 0},
    4: {"min": 0, "max": 24000, "home": 20000, "offset": 0},
    5: {"min": 0, "max": 24000, "home": 20000, "offset": 0},
    6: {"min": 0, "max": 24000, "home": 20000, "offset": 0},
}

current_pos = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}


async def callback(data):
    global current_pos
    for d in data:
        # print(d)
        servo_id = d["id"]
        angle = d["angle"]
        current_pos[servo_id] = angle
        print("servo", servo_id, "is at", angle)


async def callback_servo_offset(id, offset):
    global ranges
    print("servo", id, "has offset", offset)
    ranges[id]["offset"] = offset


async def save_ranges(the_board):

    updaters = await the_board.modules.add_hiwonder_servo(
        0, 0, 1, ids, callback, callback_servo_offset=callback_servo_offset
    )
    await asyncio.sleep(1)
    for id in ids:
        await updaters["save_offset"](id, 0)

        # await updaters["set_single_servo"](id, ranges[id]["home"], 1000)
    await asyncio.sleep(1)

    print("done!")


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
