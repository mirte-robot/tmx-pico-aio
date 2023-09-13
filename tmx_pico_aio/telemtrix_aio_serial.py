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

import aioserial
import traceback


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
        self.queue = []

    async def read(self, size=1):
        if(self.closed):
            return 0 if size == 1 else []
        if(self.serial.inWaiting()>0):
            self.queue.extend(self.serial.read_all())
        if(len(self.queue)>=size):
            data =  [self.queue.pop(0) for i in range(size)]
        else:
            if(len(self.queue) > 0):
                wait_rest = size-len(self.queue)                
                data_first = self.queue
                self.queue  = []
            else:
                wait_rest = size
                data_first = []
            try:
                data_rest = await self.serial.read_async(wait_rest)
                data = data_first + list( data_rest)
            except Exception as e:
                if(size == 1):
                    return 0
                return []
        if(size == 1):
            return data[0]
        else:
            return list(data)



    async def write(self, data):
        if(self.closed):
            return
        try:
            self.serial.write(bytes(data))
        except Exception as e:
            await self.close()
            raise e
    
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
        self.closed = True
        if self.serial:
            try:
                self.serial.close()
            except:
                pass

