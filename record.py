# Imported Libraries
import binascii
import os
import platform
import serial
import serial.tools.list_ports
import time

# Global variables
sirf = False
ver = serial.VERSION

# Write to port
def portWrite(port, str):
    if sirf:
        port.write(binascii.unhexlify(str))
    else:
        port.write(str)
    if '2.7' in ver:
        while port.outWaiting() != 0:
            pass
    elif '3.0' in ver:
        while port.out_waiting != 0:
            pass

# Read from port
def portRead(port):
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

# Change baud rate function
def changeBaud(port, rate):
    port.close()
    port.baudrate = rate
    port.open()
    port.flushInput()
    port.flushOutput()

# Main function
def main():
    # Declare global variables
    global sirf
    global ver
    
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
    
    # Open COM ports
    ports = []
    for c in coms:
        p = serial.Serial(c)
        p.flushInput()
        p.flushOutput()
        ports.append(p)
    if len(ports) != len(files):
        print 'Error: Lengths do not match'
        return
    
    # Initialize SiRF mode
    print 'Switching to SiRF mode...'
    for p in ports:
        sirf = False
        
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
        portWrite(p, '$PSRF100,0,115200,8,1,0*04\r\n')
        changeBaud(p, 115200)
        sirf = True
        # portWrite(p, 'A0A2001980000000000000000000000000000000000000000000000C1800A4B0B3') # Enable nav data
        # portWrite(p, 'A0A20002DA0000DAB0B3')    # Full power mode
        # portWrite(p, 'A0A20008A6001C010000000000C3B0B3')    # Enable MID 28
        portWrite(p, 'A0A20008A6051C010000000000C8B0B3')    # Enable MID 28
    
    # # Write data to file
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
    t = 30
    print 'Reading for {} seconds...'.format(t)
    startTime = time.time()
    # timeRequest = startTime
    timeElapsed = 0
    # timer = 0
    while timeElapsed < t:
    # while k:
        for i in range(len(ports)):
            if sirf:
                # Find start of message
                while os.stat(files[i].name).st_size == 0:
                    data = portRead(ports[i])
                    if data != 'a0':
                        continue
                    prev = data
                    data = portRead(ports[i])
                    if data != 'a2':
                        continue
                    files[i].write(prev + ' ' + data + ' ')
                    files[i].flush()
                    os.fsync(files[i])
                    break
                
                data = portRead(ports[i])
                files[i].write(data + ' ')
                
                # Find end of message
                while data == 'b0':
                    data = portRead(ports[i])
                    files[i].write(data + ' ')
                    if data != 'b3':
                        continue
                    data = portRead(ports[i])
                    if data == 'a0':
                        files[i].write('\r\n')
                    files[i].write(data + ' ')
            else:
                files[i].write(portRead(ports[i]))
        
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
    for p in ports:
        sirf = True
        portWrite(p, 'A0A20018810201010001010105010101000100010001000100012580013AB0B3')
        changeBaud(p, 9600)
        sirf = False
    
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

