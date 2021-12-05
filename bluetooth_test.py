from machine import Pin, UART
import time

uart0 = UART(0, 9600,  tx=machine.Pin(16), rx = machine.Pin(17))
uart0.write("Welcome to void loop Robot \r\n")
print("Hello Console")

led = Pin(15, Pin.OUT)

i = 0

while True:

    uart0.write("hello world \r\n")
    i = i + 1
    iSTR = str(i)
    uart0.write(iSTR)
    uart0.write( "\r\n" )
    led.toggle()
    time.sleep(1)          
