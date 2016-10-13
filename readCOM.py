# Import libraries
import argparse
import binascii
import os
import platform
import serial
import time

# Global variables
ver = serial.VERSION

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action = 'store',
                        help   = 'Data file to parse')
    parser.add_argument('time',
                        action = 'store',
                        help   = 'Recording time')
    return parser.parse_args()

# Read from port
def portRead(port, sirf):
    if '2.7' in ver:
        while port.inWaiting() == 0:
            pass
    elif '3.0' in ver:
        while port.in_waiting == 0:
            pass
    if sirf:
        return format(int(binascii.hexlify(port.read()), 16), '02x')
    else:
        return port.read()

# Main function
def main():
    # Declare global variables
    global ver
    
    # Get OS platform
    sys = platform.system()
    
    # Get arguments
    args = getArguments()
    
    # Open file
    f = open(args.file, 'ab')
    temp = args.file.split('_')[2]
    c = temp.split('.')[0]
    p = serial.Serial(c, 115200)
    if '2.7' in ver:
        p.flushInput()
        p.flushOutput()
    elif '3.0' in ver:
        p.reset_input_buffer()
        p.reset_output_buffer()
    
    t = int(args.time)
    startTime = time.time()
    timeElapsed = 0
    while timeElapsed < t:
        # Find start of message
        while os.stat(f.name).st_size == 0:
            data = portRead(p, True)
            if data != 'a0':
                continue
            prev = data
            data = portRead(p, True)
            if data != 'a2':
                continue
            f.write(prev + ' ' + data + ' ')
            f.flush()
            os.fsync(f)
            break
        
        data = portRead(p, True)
        f.write(data + ' ')
        
        # Find end of message
        while data == 'b0':
            data = portRead(p, True)
            f.write(data + ' ')
            if data != 'b3':
                continue
            data = portRead(p, True)
            if data == 'a0':
                f.write('\r\n')
            f.write(data + ' ')
        
        # Update timers
        timeElapsed = time.time() - startTime
    
    # Close file
    f.close()

if __name__ == '__main__':
    main()

