from machine import Pin, UART, I2C, SoftI2C
import time
import sys
import uos
import sdcard
from ubinascii import hexlify
import binascii
import ctypes

# declare UART channel and Baudrate for Bluetooth device
uart0 = UART(0, 9600, tx=machine.Pin(16), rx = machine.Pin(17))

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

#IMU Declaration
sda=machine.Pin(26)
scl=machine.Pin(27)
i2c = I2C(1,sda=sda,scl=scl, freq=400000)

PWR_MODE = const(0x3E)
OPR_MODE = 0X3D
UNIT_SEL = 0X3B
PAGE_ID  = 0X07

ACC_X = 0x08
ACC_Y = 0x0A
ACC_Z = 0x0C
HEAD = 0x1A

def write_imu(device, register, data):
    buf = bytearray()
    buf.append(data)
    i2c.writeto_mem(device, register, buf)

def read_imu(device, register):
    try:
        data = i2c.readfrom_mem(device[0], register, 2)
        value = int.from_bytes(data, "little")
        if(value <= 32768):
            print("ACCELERATION: ", float(value) / 16, "\n")
        else:
            buf = bytearray()
            buf.append(~data[1])
            buf.append(~data[0])
            value = float(-(int.from_bytes(buf, 'big') + 1)) / 16
    except OSError:
        None    
    return value

device = i2c.scan()
write_imu(device[0], PWR_MODE, 0x00)
write_imu(device[0], OPR_MODE, 0x00)
write_imu(device[0], UNIT_SEL, 0x00)
write_imu(device[0], OPR_MODE, 0x0C)
    
print("OPMODE: ", int.from_bytes(i2c.readfrom_mem(device[0], 0x3D, 1), "little"))
time.sleep(2)

#opens the write for the SDcard
with open("/sd/test01.csv", "w") as file:
    while True:
        
        try:
            try:
                data = i2c.readfrom_mem(device[0], HEAD, 2)
                value = int.from_bytes(data, "little")
                acceleration = str(float(value) / 100)
#                 if(value <= 32768):
#                     print("ACCELERATION1: ", float(value) / 100, "\n")
#                 else:
#                     buf = bytearray()
#                     buf.append(~data[1])
#                     buf.append(~data[0])
#                     value = float(-(int.from_bytes(buf, 'big') + 1)) / 100
#                     print("ACCELERATION2: ", value , " \n\n")
            except OSError:
                None        
            time.sleep_ms(20)
        except KeyboardInterrupt:
            break
        
        #writes to bluetooth
        uart0.write("Hello Bluetooth UART0 \r\n")
        uart0.write("Acceleration: " + acceleration + "\r\n")
    
        #writes to serial
        sys.stdout.write("Hello USB \r\n")
        sys.stdout.write("Acceleration: " + acceleration + "\r\n")
        
        #writes to CSV file on SDcard
        file.write("Acceleration, " + acceleration + "\r\n")
    
        #if power button is pressed
        if button.value():
            sys.stdout.write("Program terminated")
            uart0.write("Program terminated")
            break
    
        led.toggle() # toggle LED on and off
        time.sleep(2) # 2 second delay
    
