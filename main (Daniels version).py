from machine import Pin, UART, SoftI2C, I2C
from ubinascii import hexlify
import ctypes
import time
import sys
import uos
import sdcard

# declare UART channel and Baudrate
uart0 = UART(0, 9600, tx=machine.Pin(16), rx = machine.Pin(17))
uart1 = UART(1, 9600, tx=machine.Pin(4), rx = machine.Pin(5))

# LED GPIO Pin
led = Pin(14, Pin.OUT)

#Off button assignment
button = Pin(15, Pin.IN, Pin.PULL_DOWN)

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

#GPS Flag to see if our data is good.
good_data = True

#GPS good fix value
GPS_good_fix = "No"

#if GPS is connected to GPGGA
GPS_GPGGA_fix = True

#global variables
UTC_time = ""
sat_used = ""
latitude = ""
longitude = ""
elevation = ""
data = ""
X_ac = ""
Y_ac = ""
Z_ac = ""

X_Mag = ""
Y_Mag = ""
Z_Mag = ""

X_Gyro = ""
Y_Gyro = ""
Z_Gyro = ""

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


def write_imu(device, register, data_IMU):
    buf = bytearray()
    buf.append(data_IMU)
    i2c.writeto_mem(device, register, buf)

def read_imu(device, register):
    try:
        data_IMU = i2c.readfrom_mem(device[0], register, 18)
        value = int.from_bytes(data_IMU, "little")
        if(value <= 32768):
            print("ACCELERATION: ", float(value) / 16, "\n")
        else:
            buf = bytearray()
            buf.append(~data_IMU[1])
            buf.append(~data_IMU[0])
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
#time.sleep(2)

#opens the write for the SDcard
with open("/sd/data.csv", "w") as file:
    file.write("Good GPGGA Fix, Time, Satellites, Latitude, Longitude, Elevation MSL (m) \r\n")
    while True:
        try:
            #GPS trying to aquire data
            d = "No Data Found" if uart1.readline() is None else uart1.readline()
            
            if d is None:
                print("data is nonetype \n")
                GPS_good_fix = "No"
                GPS_GPGGA_fix = False
                data = ""
            else:
                
                if data is bytes:
                    data = d.decode()
                    
                data = str(d)
                
            #this is
            if "GPGGA" in data:
                
                #makes a string array with out data in it
                data_arr = data.split(',')
            
                #if data is missing
                if (len(data_arr) == 15):
                    hour = data_arr[1][0:2]
                    minutes = data_arr[1][2:4]
                    seconds = data_arr[1][4:8]
                    UTC_time = hour + ":" + minutes + ":" + seconds
                
                    latitude = data_arr[2]
                    longitude = data_arr[4]
                    sat_used = data_arr[7]
                    elevation = data_arr[9]
                
                    if(data_arr[1] == ""):
                        good_data = False
                        GPS_good_fix = "Partial"
                    
                    if(data_arr[2] == ""):
                        good_data = False
                        GPS_good_fix = "Partial"
                    
                    if(data_arr[4] == ""):
                        good_data = False
                        GPS_good_fix = "Partial"
                    
                    if(data_arr[7] == ""):
                        good_data = False
                        GPS_good_fix = "Partial"
                    
                    if(data_arr[9] == ""):
                        good_data = False
                        GPS_good_fix = "Partial"
                
#                 for x in data_arr:
#                     if(x == ""):
#                         good_data = False
#                         GPS_good_fix = "Partial"
                        
                    data_readout = UTC_time + " " + latitude + " " + longitude+ " " + sat_used+ " " + elevation
                    
                    if good_data:
                        GPS_good_fix = "Yes"
                        
                    else:
                        
                        GPS_good_fix = "Partial Fix"
                    
                    #Resets flag
                    good_data = True
                
                else:
                    GPS_good_fix = "Partial fix"
            else:
                GPS_GPGGA_fix = False
                data = ""
            
            data_IMU = i2c.readfrom_mem(device[0], ACC_X, 18)
            for i in range(0,18,2):
                buf = bytearray()
                buf.append(data_IMU[i])
                buf.append(data_IMU[i+1])
                value = int.from_bytes(buf, "little")
                if(value <= 32768):
                    if(i < 6):
                        value = float(value) / 100
                    else:
                        value = float(value) / 16
                else:
                    buf = bytearray()
                    buf.append(~data_IMU[i+1])
                    buf.append(~data_IMU[i])
                    value = float(-(int.from_bytes(buf, 'big') + 1)) / 100
                    if(i < 6):
                        value /= 100
                    else:
                        value /= 16
                #saves the values within the for loop
                if (i == 0):
                    X_ac = str(value)
                
                if (i == 2):
                    Y_ac = str(value)
                    
                if (i == 4):
                    Z_ac = str(value)
                    
                if (i == 6):
                    X_Mag = str(value)
                    
                if (i == 8):
                    Y_Mag = str(value)
                    
                if (i == 10):
                    Z_Mag = str(value)
                    
                if (i == 12):
                    X_Gyro = str(value)
                    
                if (i == 14):
                    Y_Gyro = str(value)
                    
                if (i == 16):
                    Z_Gyro = str(value)
               
                
                
            #writes to bluetooth
            uart0.write("Good GPGGA Fix:      " + GPS_good_fix)
            uart0.write("\r\n")
            uart0.write("Time:                " + UTC_time)
            uart0.write("\r\n")
            uart0.write("Satellites:          " + sat_used)
            uart0.write("\r\n")
            uart0.write("Latitude:            " + latitude)
            uart0.write("\r\n")
            uart0.write("Longitude:           " + longitude)
            uart0.write("\r\n")
            uart0.write("Elevation MSL (m):   " + elevation)
            uart0.write("\r\n")
            uart0.write("X accel (m/s^2):     " + X_ac)
            uart0.write("\r\n")
            uart0.write("Y accel (m/s^2):     " + Y_ac)
            uart0.write("\r\n")
            uart0.write("Z accel (m/s^2):     " + Z_ac)
            uart0.write("\r\n")
            uart0.write("X Mag (uT):          " + X_Mag)
            uart0.write("\r\n")
            uart0.write("X Mag (uT):          " + Y_Mag)
            uart0.write("\r\n")
            uart0.write("X Mag (uT):          " + Z_Mag)
            uart0.write("\r\n")
            uart0.write("X Gyro (rps.):       " + X_Gyro)
            uart0.write("\r\n")
            uart0.write("X Gyro (rps.):       " + Y_Gyro)
            uart0.write("\r\n")
            uart0.write("X Gyro (rps.):       " + Z_Gyro)
            uart0.write("\r\n")
            uart0.write("\r\n")
            uart0.write("\r\n")
            
    
            #writes to serial
            sys.stdout.write("Good GPGGA Fix:      " + GPS_good_fix + "\n")
            sys.stdout.write("Time:                " + UTC_time + "\n")
            sys.stdout.write("Satellites:          " + sat_used + "\n")
            sys.stdout.write("Latitude:            " + latitude + "\n")
            sys.stdout.write("Longitude:           " + longitude + "\n")
            sys.stdout.write("Elevation MSL (m):   " + elevation + "\n")
            sys.stdout.write("X accel (m/s^2):     " + X_ac + "\n")
            sys.stdout.write("Y accel (m/s^2):     " + Y_ac + "\n")
            sys.stdout.write("Z accel (m/s^2):     " + Z_ac + "\n")
            sys.stdout.write("X Mag (uT):          " + X_Mag + "\n")
            sys.stdout.write("Y Mag (uT):          " + Y_Mag + "\n")
            sys.stdout.write("Z Mag (uT):          " + Z_Mag + "\n")
            sys.stdout.write("X Gyro (rps.):       " + X_Gyro + "\n")
            sys.stdout.write("Y Gyro (rps.):       " + Y_Gyro + "\n")
            sys.stdout.write("Z Gyro (rps.):       " + Z_Gyro + "\n\n\n")
        
            #writes to CSV file on SDcard
            file.write(GPS_good_fix + ", " + UTC_time + ", " + sat_used + ", " + latitude + ", " + longitude + ", " + elevation + ", " + X_ac + ", " + Y_ac + ", " + Z_ac + ", " + X_Mag + ", " + Y_Mag + ", " + Z_Mag + ", " +  X_Gyro + ", " + Y_Gyro + ", " + Z_Gyro +"\r\n")
            
            #Resets Global Variables
            GPS_good_fix = "No"
            hour = ""
            minutes = ""
            seconds = ""
            UTC_time = ""
                
            latitude = ""
            longitude = ""
            sat_used = ""
            elevation = ""
            
            X_ac = ""
            Y_ac = ""
            Z_ac = ""

            X_Mag = ""
            Y_Mag = ""
            Z_Mag = ""

            X_Gyro = ""
            Y_Gyro = ""
            Z_Gyro = ""
    
            #if power button is pressed
            if button.value():
                sys.stdout.write("Program terminated")
                uart0.write("Program terminated")
                break
        except KeyboardInterrupt:
            break
        except OSError:
            None
        
        led.toggle() # toggle LED on and off
        time.sleep(0.5) # 2 second delay