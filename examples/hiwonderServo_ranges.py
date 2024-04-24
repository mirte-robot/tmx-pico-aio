"""
 Copyright (c) 2023 Arend-Jan van Hilten

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


ids = [2, 3, 4, 5, 6]
ranges = {}

updaters = {}


async def callback(data):
    global ranges
    for d in data:
        # print(d)
        servo_id = d["id"]
        angle = d["angle"]
        if not servo_id in ranges:
            ranges[servo_id] = {"min": angle, "max": angle, "id": servo_id}

        ranges[servo_id]["min"] = min(ranges[servo_id]["min"], angle)
        ranges[servo_id]["max"] = max(ranges[servo_id]["max"], angle)


async def callback_servo_range(id, range):
    print("servo", id, "has range", range)


async def read_ranges(the_board, updaters):
    for id in ids:
        print("ask ", id)
        await updaters["get_range"](id)
        await asyncio.sleep(0.5)


async def move_servo(the_board):
    global updaters
    try:
        updaters = await the_board.modules.add_hiwonder_servo(
            0, 0, 1, ids, callback, callback_servo_range=callback_servo_range
        )
        await asyncio.sleep(0.5)
        await read_ranges(the_board, updaters)
        await asyncio.sleep(0.5)
        await updaters["set_enabled_all"](False)
        while True:
            await asyncio.sleep(4)
            print(ranges)

    except KeyboardInterrupt:  # this will never trigger
        await the_board.shutdown()
        sys.exit(0)
    await the_board.shutdown()
    sys.exit(0)


async def save_ranges():
    save = int(await aioconsole.ainput("Save ranges to servos? 0/1"))
    if save:
        for k, v in ranges.items():
            await updaters["save_range"](v["id"], v["min"], v["max"])
            await asyncio.sleep(1)


# get the event loop
loop = asyncio.get_event_loop()
try:
    board = tmx_pico_aio.TmxPicoAio()
except KeyboardInterrupt:
    sys.exit()

try:
    # start the main function
    loop.run_until_complete(move_servo(board))
    loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    print("final range:", ranges)
    loop.run_until_complete(save_ranges())
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
