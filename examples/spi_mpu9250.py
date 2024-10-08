# noinspection GrazieInspection
"""
 Copyright (c) 2021 Alan Yorinks All rights reserved.

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

"""
This example initializes an MPU9250 and then reads the accelerometer
and gyro values and prints them to the screen.

The processing of the data returned from the MPU9250 is done within 
the callback functions.
"""
import asyncio

import sys

from tmx_pico_aio import tmx_pico_aio


"""
 CALLBACKS
 
 These functions process the data returned from the MPU9250
"""


async def the_device_callback(report):
    """
    Verify the device ID
    :param report: [SPI_REPORT, SPI_PORT, Number of bytes, device id]
    """
    if report[3] == 0x71:
        print("MPU9250 Device ID confirmed.")
    else:
        print(f"Unexpected device ID: {report[3]}")


# noinspection GrazieInspection
async def accel_callback(report):
    """
    Print the AX, AY and AZ values.
    :param report: [SPI_REPORT, SPI_PORT, Number of bytes, AX-msb, AX-lsb
    AY-msb, AY-lsb, AX-msb, AX-lsb]
    """
    print(
        f"AX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
        f"AY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
        f"AZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  "
    )


async def gyro_callback(report):
    # noinspection GrazieInspection
    """
    Print the GX, GY, and GZ values.

    :param report: [SPI_REPORT, SPI_PORT, Number of bytes, GX-msb, GX-lsb
    GY-msb, GY-lsb, GX-msb, GX-lsb]
    """
    print(
        f"GX = {int.from_bytes(report[3:5], byteorder='big', signed=True)}  "
        f"GY = {int.from_bytes(report[5:7], byteorder='big', signed=True)}  "
        f"GZ = {int.from_bytes(report[7:9], byteorder='big', signed=True)}  "
    )


# This is a utility function to read SPI data
async def read_data_from_device(register, number_of_bytes, callback):
    # noinspection GrazieInspection
    """
    This function reads the number of bytes using the register value.
    Data is returned via the specified callback.

    :param register: register value
    :param number_of_bytes: number of bytes to read
    :param callback: callback function
    """
    # OR in the read bit
    data = register | 0x80

    # activate chip select
    await pico.spi_cs_control(5, 0)

    # select the register
    await pico.spi_write_blocking([data], 0)
    await asyncio.sleep(0.1)

    # read the data back
    await pico.spi_read_blocking(number_of_bytes, 0, call_back=callback)

    # deactivate chip select
    await pico.spi_cs_control(5, 1)
    await asyncio.sleep(0.1)


# Convenience values for the pins.
# Note that the CS value is within a list

# These are "non-standard" pin-numbers, and therefore
# the qualify_pins parameter is set to FALSe

SPI_PORT = 0
MISO = 4
MOSI = 7
CLK = 6
CS = [5]
CS_PIN = 5

NUM_BYTES_TO_READ = 6
FREQ = 500000


async def read_mpu9250():
    # initialize the device
    await pico.set_pin_mode_spi(SPI_PORT, MISO, MOSI, CLK, FREQ, CS, qualify_pins=False)
    # reset the device
    await pico.spi_cs_control(CS_PIN, 0)
    await pico.spi_write_blocking([0x6B, 0], SPI_PORT)
    await pico.spi_cs_control(CS_PIN, 1)

    await asyncio.sleep(0.3)

    # get the device ID
    await read_data_from_device(0x75, 1, the_device_callback)
    await asyncio.sleep(0.3)

    while True:
        try:
            # get the acceleration values
            await read_data_from_device(0x3B | 0x80, 6, accel_callback)

            # get the gyro values
            await read_data_from_device(0x43 | 0x80, 6, gyro_callback)
            await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            await pico.shutdown()
            sys.exit(0)


# get the event loop
loop = asyncio.get_event_loop()
try:
    pico = tmx_pico_aio.TmxPicoAio()
except (KeyboardInterrupt, RuntimeError):
    sys.exit()

try:
    # start the main function
    loop.run_until_complete(read_mpu9250())
except KeyboardInterrupt:
    try:
        loop.run_until_complete(pico.shutdown())
        sys.exit(0)
    except RuntimeError:
        sys.exit(0)
