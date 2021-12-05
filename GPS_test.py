from machine import I2C, Pin
import time

sdaPIN = machine.Pin(20)
sclPIN = machine.Pin(21)

i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=400000)

print('Scanning i2c bus')
devices = i2c.scan()

if len(devices) == 0:
    print("No i2c device !")

else:
    print('i2c devices found:',len(devices))
    
for device in devices:
    print("Decimal address: ",device," | Hexa address: ",hex(device))
 
while True:
    i2c.readfrom(66, 16)
    print("y \r\n")
    time.sleep(2)