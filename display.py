#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import math
#import epd2in7b

from covid19 import Covid19
from storage import Storage

class Display():

    IS_DEBUG        = 'raspberrypi' not in os.uname()
    display_width   = None
    display_height  = None
    font_size       = 14
    cache_file      = 'cache.dat'
    diff_file       = 'diff.dat'
    cache_dir       = '/home/pi/pi-display/'
    font_path       = '/home/pi/pi-display/'

    covid19 = Covid19()

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
        self.covid19.refresh() 
        data = self.covid19.load()

        current_poland = next(row for row in reversed(data) if row['area'] == 'Poland')
        current_total = next(row for row in reversed(data) if row['area'] == 'Total')

        current_cases = current_poland['total_cases']
        last_cases = self._load_last()
        
        if int(current_cases) == int(last_cases):
            return None, None
        else:
            HBlackimage = self._draw_black(current_poland)
            HRedimage = self._draw_red(data, current_total)
            self._save_last(current_cases)
            return HBlackimage, HRedimage

    def commit_to_display(self, HBlackimage, HRedimage):
        if 'epd2in7b' in sys.modules:
            self.epd.Clear(0xFF)
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
            self.display_width = epd2in7b.EPD_WIDTH
            self.display_height = epd2in7b.EPD_HEIGHT

    def _draw_red(self, data, current_total):
        data_pl = [row for row in data if row['area'] == 'Poland']

        font = ImageFont.truetype(self._font_path(), self.font_size)
        HRedimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawred = ImageDraw.Draw(HRedimage)

        top_offset = 170
        x = 6
        step = math.floor((self.display_height - 6) / (len(data_pl) - 1))
        maximum = max(item['total_cases'] for item in data_pl)
        height_step = (self.display_width - 6 * 2) / maximum

        last_x = 6
        last_y = 0

        for index, item in enumerate(data_pl):
            if index == 0:
                last_y = int(item['total_cases'])
                continue
            
            y1 = top_offset - last_y * height_step
            y2 = top_offset - int(item['total_cases']) * height_step
            drawred.line((x, y1, x + step, y2), fill = 0, width = 2)
            x = x + step
            last_y = int(item['total_cases'])
        
        last_value = int(self._load_last())
        current_cases = int(data_pl[-1]['total_cases'])
        diff = current_cases - last_value
        last_diff = self._load_diff()

        if diff > 0 and diff != last_diff:
            self._save_diff(diff)

        if diff > 0:
            text = "{0} +{1}       ".format(current_cases, diff)
        else:
            text = "{0} +{1}       ".format(current_cases, last_diff)
        
        drawred.text((95, 6), text, font=font, fill = 0)
        drawred.text((95, 24), "{0}".format(current_total['total_cases']), font=font, fill = 0)
        drawred.text((95, 42), "{0}".format(data_pl[-1]['total_deaths']), font=font, fill = 0)
        
        if data_pl[-1]['total_recovered'] > 0:
            drawred.text((95, 60), "{0}".format(data_pl[-1]['total_recovered']), font=font, fill = 0)

        return HRedimage

    def _draw_black(self, last_cases):
        font = ImageFont.truetype(self._font_path(), self.font_size)
        HBlackimage = Image.new('1', (self.display_height, self.display_width), 255)
        drawblack = ImageDraw.Draw(HBlackimage)

        drawblack.line((6, 6, 6, self.display_width - 6), fill = 0)
        drawblack.line((6, self.display_width - 6, self.display_height - 6, self.display_width - 6), fill = 0)
        
        drawblack.text((10, 6), "{0}-{1:02d}-{2:02d}: ".format(last_cases['year'], last_cases['month'], last_cases['day']), font=font, fill = 0)
        drawblack.text((33, 24), "Total: ", font=font, fill = 0)
        drawblack.text((33, 42), "Deaths: ", font=font, fill = 0)
        drawblack.text((33, 60), "Healed: ", font=font, fill = 0)

        return HBlackimage

    def _save_last(self, value):
        with open(self._cache_file(), 'w') as handle:
            handle.write("%s" % value)

    def _load_last(self):
        with open(self._cache_file(), 'r') as handle:
            return handle.readline()

    def _save_diff(self, value):
        with open(self._diff_file(), 'w') as handle:
            handle.write("%s" % value)

    def _load_diff(self):
        with open(self._diff_file(), 'r') as handle:
            return handle.readline()
    
    def _cache_file(self):
        return self.cache_file if self.IS_DEBUG else self.cache_dir + self.cache_file

    def _diff_file(self):
        return self.diff_file if self.IS_DEBUG else self.cache_dir + self.diff_file

    def _font_path(self):
        return 'arialbd.ttf' if self.IS_DEBUG else '/home/pi/pi-display/arialbd.ttf' 

display = Display()
display.initialize()
black, red = display.prepare_images()
if black is not None and red is not None:
    display.commit_to_display(black, red)