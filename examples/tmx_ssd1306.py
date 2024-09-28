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


async def ssd1306(my_board):
    i2c_port = 0
    scl = 5
    sda = 4
    await my_board.set_pin_mode_i2c(i2c_port, sda, scl)
    await asyncio.sleep(0.1)
    funcs = await my_board.modules.add_tmx_ssd1306(i2c_port)
    print(funcs)
    await funcs["send_text"](
        "Hoi Martinhjklsdfjkladfsjkladfsjkladfjklsljkadfsjklfsdajkladfsjkl"
    )

    # await funcs["send_text"]("Hoi Martin")
    i = 0
    while True:
        try:
            i += 1
            await asyncio.sleep(1)
            await funcs["send_text"]("Hoi Martin" + str(i))
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
    loop.run_until_complete(ssd1306(board))
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
