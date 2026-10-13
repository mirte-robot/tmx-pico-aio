import asyncio
import sys
import time
from tmx_pico_aio import tmx_pico_aio
from adafruit_ssd1306 import _SSD1306
from PIL import Image, ImageDraw, ImageFont
import textwrap

font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 12)
import os, os.path

"""
This example sets up and control an Oled screen.
"""


class Oled(_SSD1306):
    def __init__(
        self,
        width,
        height,
        board,
        addr=0x3C,
        external_vcc=False,
        reset=None,
    ):
        self.board = board
        self.init_awaits = []
        self.write_commands = []
        self.addr = addr
        self.temp = bytearray(2)
        self.i2c_port = 0
        self.failed = False
        # Add an extra byte to the data buffer to hold an I2C data/command byte
        # to use hardware-compatible I2C transactions.  A memoryview of the
        # buffer is used to mask this byte from the framebuffer operations
        # (without a major memory hit as memoryview doesn't copy to a separate
        # buffer).
        self.buffer = bytearray(((height // 8) * width) + 1)
        # self.buffer = bytearray(16)
        # self.buffer[0] = 0x40  # Set first byte of data buffer to Co=0, D/C=1
        pin_numbers = {"sda": 4, "scl": 5}
        self.init_awaits.append(
            self.board.set_pin_mode_i2c(
                i2c_port=0,
                sda_gpio=pin_numbers["sda"],
                scl_gpio=pin_numbers["scl"],
            )
        )
        time.sleep(1)
        super().__init__(
            memoryview(self.buffer)[1:],
            width,
            height,
            external_vcc=external_vcc,
            reset=reset,
            page_addressing=False,
        )

    async def start(self):
        # Adafruit SSD1306 initializes the oled in the constructor, where async is not allowed.
        # To fix this, add all commands to a list and process them afterwards.
        for ev in self.init_awaits:
            await ev
        for cmd in self.write_commands:
            out = await self.board.i2c_write(60, cmd, i2c_port=self.i2c_port)
            if not out:
                print("write failed start")
                self.failed = True
                return

    async def set_oled_image_service(self, type, value):
        if self.failed:
            print("oled writing failed")
            return
        if type == "text":
            text = value.replace("\\n", "\n")
            image = Image.new("1", (128, 64))
            draw = ImageDraw.Draw(image)
            split_text = text.splitlines()
            lines = []
            for i in split_text:
                lines.extend(textwrap.wrap(i, width=20))

            y_text = 1
            for line in lines:
                width, height = font.getsize(line)
                draw.text((1, y_text), line, font=font, fill=255)
                y_text += height
            self.image(image)
            await self.show_async()

        if type == "image":
            await self.show_png(
                os.path.dirname(os.path.abspath(__file__))
                + "/../images/example/"
                + value
                + ".png"
            )  # open color image

        if type == "animation":
            folder = os.path.dirname(os.path.abspath(__file__)) + "/../images/example/"
            number_of_images = len(
                [
                    name
                    for name in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, name))
                ]
            )
            for i in range(number_of_images):
                print(i)
                await self.show_png(folder + value + "-" + str(i) + ".png")

    async def show_async(self):
        """Update the display"""
        xpos0 = 0
        xpos1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            xpos0 += 32
            xpos1 += 32
        if self.width == 72:
            # displays with width of 72 pixels are shifted by 28
            xpos0 += 28
            xpos1 += 28
        await self.write_cmd_async(0x21)  # SET_COL_ADDR)
        await self.write_cmd_async(xpos0)
        await self.write_cmd_async(xpos1)
        await self.write_cmd_async(0x22)  # SET_PAGE_ADDR)
        await self.write_cmd_async(0)
        await self.write_cmd_async(self.pages - 1)
        await self.write_framebuf_async()

    def show(self):
        """Update the display, only used by Adafruit library"""
        xpos0 = 0
        xpos1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            xpos0 += 32
            xpos1 += 32
        if self.width == 72:
            # displays with width of 72 pixels are shifted by 28
            xpos0 += 28
            xpos1 += 28
        self.write_cmd(0x21)  # SET_COL_ADDR)
        self.write_cmd(xpos0)
        self.write_cmd(xpos1)
        self.write_cmd(0x22)  # SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_framebuf()

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.write_commands.append([0x80, cmd])

    async def write_cmd_async(self, cmd):
        if self.failed:
            return
        self.temp[0] = 0x80
        self.temp[1] = cmd
        out = await self.board.i2c_write(60, self.temp, i2c_port=self.i2c_port)
        if not out:
            print("failed write oled")
            self.failed = True

    async def write_framebuf_async(self):
        if self.failed:
            return

        async def task(self, i):
            buf = self.buffer[i * 16 : (i + 1) * 16 + 1]
            buf[0] = 0x40
            out = await self.board.i2c_write(60, buf, i2c_port=self.i2c_port)
            if not out:
                print("failed wrcmd")
                self.failed = True

        tasks = []
        for i in range(64):
            tasks.append(task(self, i))
        await asyncio.gather(*tasks)

    def write_framebuf(self):
        for i in range(
            64
        ):  # TODO: can we have higher i2c buffer (limited by firmata 64 bits and wire 32 bits, so actually 16 bits since we need 1 bit)
            buf = self.buffer[i * 16 : (i + 1) * 16 + 1]
            buf[0] = 0x40
            self.write_commands.append(buf)

    async def show_png(self, file):
        image_file = Image.open(file)  # open color image
        image_file = image_file.convert("1", dither=Image.NONE)
        self.image(image_file)
        await self.show_async()


async def oled(board):
    oled = Oled(128, 64, board)
    await oled.start()
    await asyncio.sleep(1)
    return oled


loop = asyncio.new_event_loop()


async def main():
    try:
        board = tmx_pico_aio.TmxPicoAio(autostart=False, loop=loop)
        await board.start_aio()
        print("got board")
    except KeyboardInterrupt:
        sys.exit()
    try:
        # start the main function
        ol = await oled(board)

        await asyncio.sleep(4)

        await ol.set_oled_image_service("text", "soep")
        await asyncio.sleep(4)
        await ol.set_oled_image_service("image", "tmx-1")
        await asyncio.sleep(4)

        await ol.set_oled_image_service("animation", "tmx")
        await asyncio.sleep(4)

        await board.shutdown()
    except KeyboardInterrupt:
        await board.shutdown()
        sys.exit(0)
    except RuntimeError as e:
        print(e)
        sys.exit(0)


loop.run_until_complete(main())
