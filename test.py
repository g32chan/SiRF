# Imported Libraries
from __future__ import print_function
import binascii
import platform
import serial
import serial.tools.list_ports
import time

# Main function
def main():
    # Check PySerial Version
    ver = serial.VERSION
    print('PySerial version {} detected'.format(ver))
    
    # Get OS platform
    sys = platform.system()
    
    # Get COM ports
    print('Searching for devices...')
    coms = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if '2.7' in ver:
            if sys == 'Windows':
                if 'VID_0403+PID_6015' in p[2]:
                    com = p[0]
                    coms.append(com)
                    print('Device found on {}'.format(com))
            elif sys == 'Linux':
                if 'VID:PID=0403:6015' in p[2]:
                    com = p[0]
                    coms.append(com)
                    print('Device found on {}'.format(com))
        elif '3.0' in ver:
            if 'VID:PID=0403:6015' in p.hwid:
                com = p.device
                coms.append(com)
                print('Device found on {}'.format(com))
        else:
            print('PySerial version {} not supported'.format(ver))
            return
    if not coms:
        print('No devices found')
        return
    
    ans = ''
    while ans.lower() != 'y':
        print('Continue? (y/n) ', end = '')
        ans = raw_input()
        if ans.lower() == 'n':
            return
    
    # Open COM ports
    ports = []
    for c in coms:
        p = serial.Serial(c, timeout = 10)
        ports.append(p)
    
    # Read from ports
    t = 5
    print('Testing NMEA mode...')
    for p in ports:
        if '2.7' in ver:
            p.flushInput()
            p.flushOutput()
        elif '3.0' in ver:
            p.reset_input_buffer()
            p.reset_output_buffer()
        print('Reading port {} for {} seconds...'.format(p.port, t))
        startTime = time.time()
        timeElapsed = time.time() - startTime
        while timeElapsed < t:
            print(p.read(), end = '')
            timeElapsed = time.time() - startTime
        print()
        ans = ''
        while ans.lower() != 'y':
            print('Continue? (y/n) ', end = '')
            ans = raw_input()
            if ans.lower() == 'n':
                return
    
    print('Testing SiRF mode...')
    for p in ports:
        p.write('$PSRF100,0,115200,8,1,0*04\r\n')
        p.flush()
        p.close()
        p.baudrate = 115200
        p.open()
        if '2.7' in ver:
            p.flushInput()
            p.flushOutput()
        elif '3.0' in ver:
            p.reset_input_buffer()
            p.reset_output_buffer()
        print('Reading port {} for {} seconds...'.format(p.port, t))
        startTime = time.time()
        timeElapsed = time.time() - startTime
        while timeElapsed < t:
            temp = p.read()
            if temp != '':
                print(format(int(binascii.hexlify(temp), 16), '02x'), end = '')
            timeElapsed = time.time() - startTime
        p.write(binascii.unhexlify('A0A20018810201010001010105010101000100010001000100012580013AB0B3'))
        p.flush()
        p.close()
        p.baudrate = 9600
        p.open()
        print()
        ans = ''
        while ans.lower() != 'y':
            print('Continue? (y/n) ', end = '')
            ans = raw_input()
            if ans.lower() == 'n':
                return
    
    # Shut down chip
    print('Shut down? (y/n) ', end = '')
    ans = raw_input()
    if ans.lower() == 'y':
        print('Shutting down devices...')
        for p in ports:
            p.write('$PSRF117,16*0B\r\n')
            p.flush()
    
    # Close ports
    for p in ports:
        p.close()

if __name__ == '__main__':
    main()

