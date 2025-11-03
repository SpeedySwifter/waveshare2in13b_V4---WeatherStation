"""
Waveshare 2.13inch e-Paper V4 Display Driver (Regular Black/White version)
Compatible with Raspberry Pi
"""

import logging
import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

logger = logging.getLogger(__name__)

class EPD:
    def __init__(self):
        self.reset_pin = 17
        self.dc_pin = 25
        self.cs_pin = 8
        self.busy_pin = 24
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        spi.writebytes(data)

    def module_init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.busy_pin, GPIO.IN)
        
        global spi
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 4000000
        spi.mode = 0b00
        return 0

    def module_exit(self):
        logging.debug("spi end")
        spi.close()

        logging.debug("close 5V, Module enters 0 power consumption ...")
        GPIO.output(self.reset_pin, 0)
        GPIO.output(self.dc_pin, 0)

        GPIO.cleanup()

    def reset(self):
        GPIO.output(self.reset_pin, 1)
        self.delay_ms(20) 
        GPIO.output(self.reset_pin, 0)
        self.delay_ms(2)
        GPIO.output(self.reset_pin, 1)
        self.delay_ms(20)   

    def send_command(self, command):
        GPIO.output(self.dc_pin, 0)
        GPIO.output(self.cs_pin, 0)
        self.spi_writebyte([command])
        GPIO.output(self.cs_pin, 1)

    def send_data(self, data):
        GPIO.output(self.dc_pin, 1)
        GPIO.output(self.cs_pin, 0)
        self.spi_writebyte([data])
        GPIO.output(self.cs_pin, 1)
        
    def send_data2(self, data):
        GPIO.output(self.dc_pin, 1)
        GPIO.output(self.cs_pin, 0)
        self.spi_writebyte(data)
        GPIO.output(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = GPIO.input(self.busy_pin)
        timeout = 0
        while(busy == 0 and timeout < 100):
            self.send_command(0x71)
            busy = GPIO.input(self.busy_pin)
            timeout += 1
            self.delay_ms(10)
        if timeout >= 100:
            logger.warning("Display busy timeout - display may not be connected")
        self.delay_ms(20)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.delay_ms(100)
        self.ReadBusy()

    def init(self):
        if (self.module_init() != 0):
            return -1
        
        self.reset()
        
        self.send_command(0x04)
        self.ReadBusy()

        self.send_command(0x00)
        self.send_data(0x0f)
        self.send_data(0x89)

        self.send_command(0x61)
        self.send_data(0x7A)
        self.send_data(0x00)
        self.send_data(0xFA)

        self.send_command(0x50)
        self.send_data(0x77)

        return 0

    def getbuffer(self, image):
        buf = [0xFF] * (int(self.width/8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        
        logger.debug("imwidth = %d, imheight = %d",imwidth, imheight)
        if(imwidth == self.width and imheight == self.height):
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, image):
        self.send_command(0x10)
        self.send_data2([0x00] * int(self.width * self.height / 8))
        
        self.send_command(0x13)
        self.send_data2(image)
        
        self.TurnOnDisplay()

    def Clear(self):
        self.send_command(0x10)
        self.send_data2([0x00] * int(self.width * self.height / 8))
        
        self.send_command(0x13)
        self.send_data2([0xFF] * int(self.width * self.height / 8))
        
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02)
        self.ReadBusy()
        
        self.send_command(0x07)
        self.send_data(0xA5)
        
        self.module_exit()
