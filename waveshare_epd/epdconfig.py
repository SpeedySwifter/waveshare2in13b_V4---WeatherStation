"""
E-Paper configuration module for Raspberry Pi
Based on official Waveshare implementation
"""

import os
import logging
import sys
import time

# Pin definition
RST_PIN         = 17
DC_PIN          = 25
CS_PIN          = 8
BUSY_PIN        = 24

# SPI device
SPI_DEVICE      = 0

logger = logging.getLogger(__name__)

def module_init():
    global spi, GPIO
    try:
        import spidev
        import RPi.GPIO as GPIO
    except ImportError:
        logger.error("This library requires the spidev and RPi.GPIO libraries")
        logger.error("Install with: sudo apt install python3-spidev python3-rpi.gpio")
        return -1

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)

    # SPI device, bus = 0, device = 0
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 4000000
    spi.mode = 0b00
    return 0

def module_exit():
    logger.debug("spi end")
    spi.close()

    logger.debug("close 5V, Module enters 0 power consumption ...")
    GPIO.output(RST_PIN, 0)
    GPIO.output(DC_PIN, 0)
    GPIO.cleanup()

def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    spi.writebytes(data)

def spi_writebyte2(data):
    spi.writebytes(data)
