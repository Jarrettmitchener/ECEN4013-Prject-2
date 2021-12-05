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
            uart0.write("\r\n")
            uart0.write("\r\n")
            
    
            #writes to serial
            sys.stdout.write("Good GPGGA Fix:      " + GPS_good_fix + "\n")
            sys.stdout.write("Time:                " + UTC_time + "\n")
            sys.stdout.write("Satellites:          " + sat_used + "\n")
            sys.stdout.write("Latitude:            " + latitude + "\n")
            sys.stdout.write("Longitude:           " + longitude + "\n")
            sys.stdout.write("Elevation MSL (m):   " + elevation + "\n\n\n")
        
            #writes to CSV file on SDcard
            file.write(GPS_good_fix + ", " + UTC_time + ", " + sat_used + ", " + latitude + ", " + longitude + ", " + elevation + "\r\n")
            
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
    
            #if power button is pressed
            if button.value():
                sys.stdout.write("Program terminated")
                uart0.write("Program terminated")
                break
        except KeyboardInterrupt:
            break
        
        led.toggle() # toggle LED on and off
        time.sleep(0.5) # 2 second delay
    