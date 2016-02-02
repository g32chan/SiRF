# Imported Libraries
import binascii
import platform
import serial
import serial.tools.list_ports

# Write to port
def portWrite(port, str):
    port.write(binascii.unhexlify(str))
    while port.outWaiting() != 0:
        pass

# Main function
def main():
    # Get OS platform
    sys = platform.system()
    
    # Get COM ports
    print 'Searching for device...'
    coms = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
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
    if not coms:
        print 'Device not found'
        return
    
    # Open COM ports
    ports = []
    for c in coms:
        p = serial.Serial(c, baudrate = 115200)
        p.flushInput()
        p.flushOutput()
        ports.append(p)
    
    # Shut down chip
    print 'Shutting down devices...'
    for p in ports:
        portWrite(p, 'A0A20002CD1000DDB0B3')
    
    # Close ports
    for p in ports:
        p.close()

if __name__ == '__main__':
    main()

