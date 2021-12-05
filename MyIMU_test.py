import time
import machine
import adafruit_bno055
sda=machine.Pin(26)
scl=machine.Pin(27)
i2c = I2C(1,sda=sda,scl=scl, freq=400000)

last_val = 0xFFFF



