from utime import sleep,sleep_ms
import time
import uasyncio as asyncio
import sh1106
from machine import Pin,I2C
from IO import sda,scl
from writer import Writer
import freesans20
import courier20

# Display Initialization
i2c=I2C(1,sda=sda, scl=scl)
width=128
height=64 
oled = sh1106.SH1106_I2C(width, height, i2c, Pin(4), 0x3c)
Font_Thin = Writer(oled, freesans20)
Font_Thick = Writer(oled, courier20)

# Permanent Data Storage File
file=open("Log.txt", "r+")
log=file.read()

# Global Variables
start=bool(int(log[0]))
min=int(log[1])
max=int(log[2])
over=bool(int(log[3]))
level=1
power=False
starting=False
filling=False
overflowing=False
over_timer=0