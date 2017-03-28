# Import libraries
import argparse
import binascii
import platform
import serial
import threading
import time

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action = 'store',
                        help   = 'Data file to parse')
    parser.add_argument('baud',
                        action = 'store',
                        help   = 'Serial port baud rate')
    parser.add_argument('time',
                        action = 'store',
                        help   = 'Recording time')
    return parser.parse_args()

# Reader
def reader(port, t):
    timeElapsed = 0
    startTime = time.time()
    while timeElapsed < t:
        # try:
        data = format(int(binascii.hexlify(port.read()), 16), '02x')
        buffer.append(data)
        # except:
            # pass
        timeElapsed = time.time() - startTime
    # print 'Reader done', len(buffer)

# Writer
def writer(fid, t):
    timeElapsed = 0
    startTime = time.time()
    while timeElapsed < t or buffer:
    # while timeElapsed < t:
        # print len(buffer)
        try:
            temp = buffer.pop(0)
            fid.write(temp)
        except:
            pass
        timeElapsed = time.time() - startTime
    # print 'Writer done', len(buffer)

# Main function
def main():
    # Get arguments
    args = getArguments()
    
    # Get OS platform
    sys = platform.system()
    
    # Open file
    f = open(args.file, 'ab')
    
    # Open port
    baud = int(args.baud)
    temp = args.file.split('_')[2]
    c = temp.split('.')[0]
    if sys == 'Linux':
        c = '/dev/' + c
    p = serial.Serial(c, baud)
    p.reset_input_buffer()
    p.reset_output_buffer()
    
    # # Log data
    # t = int(args.time)
    # timeElapsed = 0
    # startTime = time.time()
    # while timeElapsed < t:
        # f.write(format(int(binascii.hexlify(p.read()), 16), '02x'))
        # timeElapsed = time.time() - startTime
    
    # Create threads
    global buffer
    buffer = []
    t = int(args.time)
    jobs = []
    jobs.append(threading.Thread(target = reader, args = (p, t)))
    jobs.append(threading.Thread(target = writer, args = (f, t)))
    
    # Log data
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
    
    # Close port
    p.close()
    
    # Close file
    f.close()

if __name__ == '__main__':
    main()

