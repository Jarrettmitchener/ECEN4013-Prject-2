import time
from machine import Pin
from machine import UART

uart1 = UART(0, 115200)

led = Pin(15, Pin.OUT)

while True:
    uart1.write("This is a serial test \r\n")
    led.toggle()
    time.sleep(2)
