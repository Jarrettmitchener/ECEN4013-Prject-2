import time
from machine import Pin
import sys

led = Pin(15, Pin.OUT)

while True:
    
    sys.stdout.write("This is a USB test \r\n")
    
    #LED toggle to see if board is physically working
    led.toggle()
    time.sleep(1)
