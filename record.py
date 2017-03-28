# Imported Libraries
import argparse
import binascii
import os
import platform
import serial
import serial.tools.list_ports
import subprocess as sp
import threading
import time

# Global variables
# sirf = False
ver = serial.VERSION

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--thread',
                        action = 'store_true',
                        help   = 'Use threads')
    parser.add_argument('baud',
                        action = 'store',
                        help   = 'Serial port baud rate')
    parser.add_argument('time',
                        action = 'store',
                        help   = 'Recording time')
    return parser.parse_args()

# Write to port
def portWrite(port, str, sirf):
    if sirf:
        port.write(binascii.unhexlify(str))
    else:
        port.write(str)
    port.flush()
    # if '2.7' in ver:
        # while port.outWaiting() != 0:
            # pass
    # elif '3.0' in ver:
        # while port.out_waiting != 0:
            # pass

# # Read from port
# def portRead(port, sirf):
    # if '2.7' in ver:
        # while port.inWaiting() == 0:
            # pass
    # elif '3.0' in ver:
        # while port.in_waiting == 0:
            # pass
    # if sirf:
        # return format(int(binascii.hexlify(port.read()), 16), '02x')
    # else:
        # return port.read()

# Change baud rate function
def changeBaud(port, rate):
    port.close()
    port.baudrate = rate
    port.open()
    if '2.7' in ver:
        port.flushInput()
        port.flushOutput()
    elif '3.0' in ver:
        port.reset_input_buffer()
        port.reset_output_buffer()

# Reader
def reader(port, t, buffer):
    timeElapsed = 0
    startTime = time.time()
    while timeElapsed < t:
        try:
            data = format(int(binascii.hexlify(port.read()), 16), '02x')
            buffer.append(data)
        except:
            pass
        timeElapsed = time.time() - startTime
    # print 'Reader done', len(buffer)

# Writer
def writer(fid, t, buffer):
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
    # Declare global variables
    # global sirf
    global ver
    global buffer
    
    # Get arguments
    args = getArguments()
    
    # Get OS platform
    sys = platform.system()
    
    # Get COM ports
    print 'Searching for devices...'
    coms = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if '2.7' in ver:
            if sys == 'Windows':
                if 'VID_0403+PID_6015' in p[2]:
                    com = p[0]
                    coms.append(com)
                    print 'Device found on {}'.format(com)
            elif sys == 'Linux':
                if 'VID:PID=0403:6015' in p[2]:
                    com = p[0]
                    coms.append(com)
                    print 'Device found on {}'.format(com)
        elif '3.0' in ver:
            if 'VID:PID=0403:6015' in p.hwid:
                com = p.device
                coms.append(com)
                print 'Device found on {}'.format(com)
        else:
            print 'PySerial version unrecognized'
            return
    if not coms:
        print 'No devices found'
        return
    
    # Create data files
    files = []
    for c in coms:
        curTime = time.strftime("%d%m%y_%H%M%S", time.gmtime())
        if sys == 'Windows':
            fileName = '{}_{}.dat'.format(curTime, c)
        elif sys == 'Linux':
            fileName = '{}_{}.dat'.format(curTime, c.split('/')[2])
        f = open(fileName, 'ab')
        files.append(f)
        # if args.thread:
            # f.close()
    
    # Open COM ports
    ports = []
    for c in coms:
        p = serial.Serial(c, timeout = 0)
        if '2.7' in ver:
            p.flushInput()
            p.flushOutput()
        elif '3.0' in ver:
            p.reset_input_buffer()
            p.reset_output_buffer()
        ports.append(p)
    if len(ports) != len(files):
        print 'Error: Lengths do not match'
        return
    
    # Initialize SiRF mode
    print 'Switching to SiRF mode...'
    baud = int(args.baud)
    if baud == 9600:
        checksum = '0C'
    elif baud == 19200:
        checksum = '39'
    elif baud == 38400:
        checksum = '3C'
    elif baud == 57600:
        checksum = '37'
    elif baud == 115200:
        checksum = '04'
    elif baud == 230400:
        checksum = '06'
    else:
        print 'Error: Input baud rate not supported'
        return
    
    for p in ports:
        # sirf = False
        
        # # Check current mode
        # prev = ''
        # data = portRead(p)
        # while prev != '\r' and data != '\n':
            # prev = data
            # data = portRead(p)
            # prevHex = format(int(binascii.hexlify(prev), 16), '02x')
            # dataHex = format(int(binascii.hexlify(data), 16), '02x')
            # if prevHex == 'a0' and dataHex == 'a2':
                # sirf = True
                # break
        
        # if not sirf:
        portWrite(p, '$PSRF100,0,' + str(baud) + ',8,1,0*' + checksum + '\r\n', False)
        changeBaud(p, baud)
        # sirf = True
        # portWrite(p, 'A0A2001980000000000000000000000000000000000000000000000C1800A4B0B3') # Enable nav data
        # portWrite(p, 'A0A20002DA0000DAB0B3')    # Full power mode
        # portWrite(p, 'A0A20008A6001C010000000000C3B0B3')    # Enable MID 28
        for i in range(10):
            portWrite(p, 'A0A20008A6051C010000000000C8B0B3', True) # Enable MID 28
        # if args.thread:
            # p.close()
    
    # Write data to file
    # k = 1048576 # 1 MB
    # k = 512000  # 500 KB
    # k = 102400  # 100 KB
    # k = 51200   # 50 KB
    # k = 25600   # 25 KB
    # k = 10240   # 10 KB
    # k = 1024    # 1 KB
    # # k = 512     # 512 Bytes
    # # k = 256     # 256 Bytes
    # total = k
    # print 'Reading {} bytes...'.format(k)
    # prev = ''
    # x = 10
    # sub = []
    jobs = []
    # t = 60
    t = int(args.time)
    timeElapsed = 0
    print 'Reading for {} seconds...'.format(t)
    startTime = time.time()
    # timeRequest = startTime
    # timer = 0
    if args.thread:
        buffer = []
        for i in range(len(ports)):
            buffer.append([])
            jobs.append(threading.Thread(target = reader, args = (ports[i], t, buffer[i])))
            jobs.append(threading.Thread(target = writer, args = (files[i], t, buffer[i])))
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
            # # s = sp.Popen('python readCOM.py ' + files[i].name + ' ' + str(baud) + ' ' + str(t), stdout = sp.PIPE, stderr = sp.PIPE)
            # s = sp.Popen(['python', 'readCOM.py', files[i].name, str(baud), str(t)], stdout = sp.PIPE, stderr = sp.PIPE)
            # sub.append(s)
        # for s in sub:
            # s.wait()
        print 'Threads closed'
    else:
        while timeElapsed < t:
        # while k:
            for i in range(len(ports)):
                try:
                    files[i].write(format(int(binascii.hexlify(ports[i].read()), 16), '02x'))
                except:
                    pass
                # # if sirf:
                    # # Find start of message
                    # while os.stat(files[i].name).st_size == 0:
                        # data = portRead(ports[i], True)
                        # if data != 'a0':
                            # continue
                        # prev = data
                        # data = portRead(ports[i], True)
                        # if data != 'a2':
                            # continue
                        # files[i].write(prev + ' ' + data + ' ')
                        # files[i].flush()
                        # os.fsync(files[i])
                        # break
                    
                    # data = portRead(ports[i], True)
                    # files[i].write(data + ' ')
                    
                    # # Find end of message
                    # while data == 'b0':
                        # data = portRead(ports[i], True)
                        # files[i].write(data + ' ')
                        # if data != 'b3':
                            # continue
                        # data = portRead(ports[i], True)
                        # if data == 'a0':
                            # files[i].write('\r\n')
                        # files[i].write(data + ' ')
                # # else:
                    # # files[i].write(portRead(ports[i]))
        
            # Update timers
            timeElapsed = time.time() - startTime
            # timer = time.time() - timeRequest
        
            # # Request Ephemeris Data
            # if sirf and timer > 1:
                # for p in ports:
                    # portWrite(p, 'A0A200039300000093B0B3')    # Send MID 147
                # timeRequest = time.time()
            
            # # Print percent completed
            # if total >= 100:
                # if 100 * (total - k) / total == x:
                    # print '{}% complete (Bytes remaining: {})'.format(x, k)
                    # x += 10
            # k -= 1
    # print '100% complete'
    print 'Finished reading from devices'
    
    # Switch back to NMEA
    print 'Reverting to NMEA mode...'
    ports = []
    for c in coms:
        p = serial.Serial(c, baud)
        if '2.7' in ver:
            p.flushInput()
            p.flushOutput()
        elif '3.0' in ver:
            p.reset_input_buffer()
            p.reset_output_buffer()
        ports.append(p)
    
    for p in ports:
        # sirf = True
        portWrite(p, 'A0A20018810201010001010105010101000100010001000100012580013AB0B3', True)
        changeBaud(p, 9600)
        # sirf = False
    
    # # Shut down chip
    # print 'Shutting down devices...'
    # for p in ports:
        # if sirf:
            # portWrite(p, 'A0A20002CD1000DDB0B3')
            # # print portRead(p, sirf)
            
            # # # Switch back to NMEA
            # # portWrite(p, 'A0A20018810201010001010105010101000100010001000100012580013AB0B3')
            # # changeBaud(p, 9600)
            # # sirf = False
            # # portWrite(p, '$PSRF117,16*0B\r\n')
        # else:
            # portWrite(p, '$PSRF117,16*0B\r\n')
    
    # Close ports
    for p in ports:
        p.close()
    
    # Close files
    for f in files:
        f.close()

if __name__ == '__main__':
    main()

