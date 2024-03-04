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


ids = range(1, 20)
found = []


async def callback_verify_id(vid, ok):
    global found
    # print(vid, ok)
    if ok > 0:
        print("found", vid)
        found.append(vid)


async def check_servos(the_board):
    try:
        updaters = await the_board.modules.add_hiwonder_servo(
            0, 0, 1, [], callback_id_verify=callback_verify_id
        )
        await asyncio.sleep(0.5)
        for x in ids:
            # print("check ", x)
            await updaters["verify_id"](x)
            await asyncio.sleep(0.1)
        print("All ids:", found)

    except KeyboardInterrupt:
        await the_board.shutdown()
        print(ranges)
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
    loop.run_until_complete(check_servos(board))
    loop.run_until_complete(board.reset_board())
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
