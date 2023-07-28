# -*- coding: utf-8 -*-
"""
 Copyright (c) 2015-2020 Alan Yorinks All rights reserved.

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
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import asyncio
import sys
import serial
import time
LF = 0x0a
import aioserial

class TelemetrixAioSerial:
    def __init__(self, com_port='/dev/ttyACM0', baud_rate=115200, sleep_tune=.0001,
                 telemetrix_aio_instance=None, close_loop_on_error=True, loop = None):
        self.com_port = com_port
        self.sleep_tune = sleep_tune
        self.telemetrix_aio_instance = telemetrix_aio_instance
        self.close_loop_on_error = close_loop_on_error
        self.baud_rate = baud_rate
        self.closed = False
        self.serial = aioserial.AioSerial(port=com_port, baudrate=baud_rate, cancel_write_timeout=1, cancel_read_timeout=1, loop=loop)

    async def read(self, size=1):
        # print("start read s", size)
        try:
            data = await self.serial.read_async(size)
        except Exception as e:
            if(self.closed):
                return 0
            print(e)
            if(size == 1):
                return 0
            return []
        # print("received ", data)
        if(size == 1):
            return ord(data)
        else:
            return list(data)



    async def write(self, data):
        x = await self.serial.write_async(bytes(data))
        return x
    
    async def reset_input_buffer(self):
        """
        Reset the input buffer
        """
        self.serial.reset_input_buffer()

    async def reset_output_buffer(self):
        """
        Reset the output buffer
        """
        self.serial.reset_output_buffer()

    async def close(self):
        """
        Close the serial port
        """
        if self.serial:
            self.serial.close()

