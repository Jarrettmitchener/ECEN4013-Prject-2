from machine import Pin, UART
import time
import sys

# declare UART channel and Baudrate
uart1 = UART(1, 9600, tx=machine.Pin(4), rx = machine.Pin(5))

#GPS Flag to see if our data is good.
good_data = True

#GPS good fix value
GPS_good_fix = ""

#if GPS is connected to GPGGA
GPS_GPGGA_fix = True

while True:
    try:
        d = "No Data Found" if uart1.readline() is None else uart1.readline()
        if(d == "No Data Found"):
            GPS_good_fix = "No"
            GPS_GPGGA_fix = False
            data = ""
            
        else:
            data = d.decode()
                    
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
                print(data_readout + "\r\n")
                if good_data:
                    GPS_good_fix = "Yes"
                    print(data + " WE GOT A GOOD FIX" + "\r\n")
                else:
                    print("Partial fix, Data not good \r\n")
                    
                #Resets flag
                good_data = True
                
            else:
                print("no good fix")
        else:
            GPS_GPGGA_fix = False
            data = ""
        
    except KeyboardInterrupt:
        break
    
    time.sleep(0.5)