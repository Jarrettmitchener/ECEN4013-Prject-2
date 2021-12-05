import machine
import sdcard
import uos
import time
from machine import Pin

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(9, machine.Pin.OUT)

#button assignment
button = Pin(0, Pin.IN, Pin.PULL_DOWN)

# Intialize SPI peripheral (start with 1 MHz)
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

i = 0
# Create a file and write something to it
with open("/sd/test01.csv", "w") as file:
    while True:
        file.write("DATA, Data2 \r\n")
        time.sleep(1)
        i = i + 1
        if button.value():
            print("terminated")
            break

# Open the file we just created and read from it
# with open("/sd/test01.csv", "r") as file:
#     data = file.read()
#     print(data)