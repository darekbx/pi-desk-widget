#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

from covid19 import Covid19

class Display():

    IS_DEBUG        = True
    display_width   = None
    display_height  = None
    font_size       = 12

    def initialize(self):
        if self.IS_DEBUG:
            self.display_width = 176
            self.display_height = 264
        else:
            import epd2in7b

        try:
            self._initialize_display()
        except :
            print ('traceback.format_exc():\n%s',traceback.format_exc())
            exit()

    def prepare_images(self):

        data = Covid19().load()[::-1]

        HBlackimage = self._draw_black(data)
        HRedimage = self._draw_red(data)
        return HBlackimage, HRedimage

    def commit_to_display(self, HBlackimage, HRedimage):
        if 'epd2in7b' in sys.modules:
            self.epd.display(self.epd.getbuffer(HBlackimage), self.epd.getbuffer(HRedimage))
            self.epd.sleep()
        else:
            concated_image = Image.new('RGBA', (HBlackimage.width, HBlackimage.height))
            concated_image.paste(HBlackimage, (0, 0))

            red_data = HRedimage.load()            
            for x in range(HBlackimage.width):
                for y in range(HBlackimage.height):
                    color = red_data[x, y]
                    if color == 0:
                        concated_image.putpixel((x, y), (255, 0, 0))

            concated_image.show()
    
    def _initialize_display(self):
        if 'epd2in7b' in sys.modules:
            self.epd = epd2in7b.EPD()
            self.epd.init()
            self.epd.Clear(0xFF)
            self.display_width = epd2in7b.EPD_WIDTH
            self.display_height = epd2in7b.EPD_HEIGHT

    def _draw_red(self, data):
        font = ImageFont.truetype('ObliviousFont.ttf', self.font_size)
        HRedimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawred = ImageDraw.Draw(HRedimage)

        y = 12
        x = 150
        for item in data:
            drawred.text((x, y), "%s" % item['cases'], font=font, fill = 0)
            y += 15

        return HRedimage

    def _draw_black(self, data):
        font = ImageFont.truetype('ObliviousFont.ttf', self.font_size)
        HBlackimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawblack = ImageDraw.Draw(HBlackimage)

        y = 12
        x = 10
        for item in data:
            drawblack.text((x, y), item['date'], font=font, fill = 0)
            y += 15

        return HBlackimage

display = Display()
display.initialize()
black, red = display.prepare_images()
display.commit_to_display(black, red)