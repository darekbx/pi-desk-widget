#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import math
import epd2in7b

from covid19 import Covid19

class Display():

    IS_DEBUG        = False
    display_width   = None
    display_height  = None
    font_size       = 16
    cache_file      = 'cache.dat'
    cache_dir       = '/home/pi/display/'
    font_path       = '/home/pi/pi-display/'

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

        if self.IS_DEBUG:
            data = [
                { 'date': '2020-03-01', 'cases': 1},
                { 'date': '2020-03-01', 'cases': 2},
                { 'date': '2020-03-01', 'cases': 5},
                { 'date': '2020-03-01', 'cases': 10},
                { 'date': '2020-03-01', 'cases': 32},
                { 'date': '2020-03-01', 'cases': 44},
                { 'date': '2020-03-10', 'cases': 58},
                { 'date': '2020-03-11', 'cases': 104}
            ]
        else:
            data = Covid19().load()

        HBlackimage = self._draw_black(data)
        HRedimage = self._draw_red(data)

        self._save_last(data[-1]['cases'])

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
        font = ImageFont.truetype(self._font_path(), self.font_size)
        HRedimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawred = ImageDraw.Draw(HRedimage)

        top_offset = 170
        x = 6
        step = math.floor((self.display_height - 6) / (len(data) - 1))
        maximum = max(item['cases'] for item in data)
        height_step = (self.display_width - 6 * 2) / maximum

        last_x = 6
        last_y = 0

        for index, item in enumerate(data):
            if index == 0:
                last_y = int(item['cases'])
                continue
            
            y1 = top_offset - last_y * height_step
            y2 = top_offset - int(item['cases']) * height_step
            drawred.line((x, y1, x + step, y2), fill = 0, width = 2)
            x = x + step
            last_y = int(item['cases'])
        
        last_value = int(self._load_last())
        current_cases = int(data[-1]['cases'])
        diff = current_cases - last_value

        if diff > 0:
            text = "{0} +{1}     ".format(current_cases, diff)
        else:
            text = "{0}    ".format(current_cases)
        drawred.text((130, 6), text, font=font, fill = 0)

        return HRedimage

    def _draw_black(self, data):
        font = ImageFont.truetype(self._font_path(), self.font_size)
        HBlackimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawblack = ImageDraw.Draw(HBlackimage)

        drawblack.line((6, 6, 6, self.display_width - 6), fill = 0)
        drawblack.line((6, self.display_width - 6, self.display_height - 6, self.display_width - 6), fill = 0)

        drawblack.text((10, 6), "%s:    " % data[-1]['date'], font=font, fill = 0)

        return HBlackimage

    def _save_last(self, value):
        with open(self._cache_file(), 'w') as handle:
            handle.write("%s" % value)

    def _load_last(self):
        with open(self._cache_file(), 'r') as handle:
            return handle.readline()

    def _cache_file(self):
        return self.cache_file if self.IS_DEBUG else self.cache_dir + self.cache_file

    def _font_path(self):
        return 'theboldfont.ttf' if self.IS_DEBUG else '/home/pi/pi-display/theboldfont.ttf' 

display = Display()
display.initialize()
black, red = display.prepare_images()
display.commit_to_display(black, red)