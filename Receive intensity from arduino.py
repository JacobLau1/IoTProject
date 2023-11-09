#!/usr/bin/env python3
import serial
if __name__ == '__main__':
    #change /dev/ttyACM0 to the port we're using
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            intensity = ser.readline().decode('utf-8').rstrip()
            print(intensity)
            
            if(int(intensity) < 400):
                print("Turn on LED and send email")