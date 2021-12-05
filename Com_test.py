from machine import Pin, UART
import time
import sys
import uos
import sdcard

# declare UART channel and Baudrate
uart0 = UART(0, 9600, tx=machine.Pin(16), rx = machine.Pin(17))
uart1 = UART(1, 9600, tx=machine.Pin(4), rx = machine.Pin(5))

# LED GPIO Pin
led = Pin(15, Pin.OUT)

#Off button assignment
button = Pin(28, Pin.IN, Pin.PULL_DOWN)

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(9, machine.Pin.OUT)

#Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(8))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

#opens the write for the SDcard
with open("/sd/test01.csv", "w") as file:
    while True:
        #writes to bluetooth
        uart0.write("Hello Bluetooth UART0 \r\n")
        uart1.write("Hello Bluetooth UART1 \r\n")
    
        #writes to serial
        sys.stdout.write("Hello USB \r\n")
        
        #writes to CSV file on SDcard
        file.write("Hello, SDcard \r\n")
    
        #if power button is pressed
        if button.value():
            sys.stdout.write("Program terminated")
            uart0.write("Program terminated")
            break
    
        led.toggle() # toggle LED on and off
        time.sleep(0.5) # 2 second delay
    