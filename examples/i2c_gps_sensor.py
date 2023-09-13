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
import pynmea2

"""
This example sets up and control an ADXL345 i2c accelerometer.
It will continuously print data the raw xyz data from the device.
"""

# the call back function to print the gps data

current_sentence = ""

def the_callback(data):
    global current_sentence
    chars = map(lambda d: chr(d), data)
    current_sentence += "".join(chars)
    # if(len(current_sentence)>100):
    # print(current_sentence)
    if "\n" in current_sentence:
        sentence = current_sentence.splitlines()
        # print(sentence[0])
        if len(sentence) > 1:
            current_sentence = sentence[1]
        else:
            current_sentence = ""
        
        try: # first sentence is always broken
            msg = pynmea2.parse(sentence[0])
        except:
            return
        if msg.sentence_type == "GGA":
            print(msg.latitude, msg.longitude)
        if msg.sentence_type == 'RMC':
            print("Speed", msg.spd_over_grnd)
        if msg.sentence_type == 'TXT':
            print(msg)
        

    # print(''.join(chars), end='')


async def gps(my_board):
    await asyncio.sleep(0.1)
    await my_board.sensors.add_gps(rx=5, tx=4, uart_channel=1, callback=the_callback)
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
    loop.run_until_complete(gps(board))
    print("done mpu")
except KeyboardInterrupt:
    loop.run_until_complete(board.shutdown())
    sys.exit(0)
except RuntimeError as e:
    print(e)
    sys.exit(0)
