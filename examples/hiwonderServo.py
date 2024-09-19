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

from tmx_pico_aio import tmx_pico_aio


async def callback(data):
    for d in data:
        print(d)


async def move_servo(the_board):
    try:
        updaters = await the_board.modules.add_hiwonder_servo(
            1, 4, 5, [3, 4, 5], callback
        )
        set_single_servo = updaters["set_single_servo"]
        set_multiple_servos = updaters["set_multiple_servos"]
        await asyncio.sleep(4)
        # await set_single_servo(4, 2000, 1000)

        # await asyncio.sleep(4)
        # await set_single_servo(4, 4000, 1000)
        # await asyncio.sleep(2)
        # await set_single_servo(3, 10000, 1000)

        # await asyncio.sleep(4)
        # await set_single_servo(3, 13000, 1000)
        # await asyncio.sleep(5)
        # # will send the commands to all and then start the servos
        # await set_multiple_servos(
        #     [
        #         {"id": 3, "angle": 10000, "time": 2000},
        #         {"id": 4, "angle": 2000, "time": 3000},
        #     ]
        # )
        await asyncio.sleep(5)

    except KeyboardInterrupt:
        await the_board.shutdown()
        sys.exit(0)

    await the_board.shutdown()
    sys.exit(0)


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
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
