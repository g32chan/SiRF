# Imported Libraries
import platform
import serial
import serial.tools.list_ports

# Global variables
ver = serial.VERSION

# Write to port
def portWrite(port, str):
    port.write(str)
    if '2.7' in ver:
        while port.outWaiting() != 0:
            pass
    elif '3.0' in ver:
        while port.out_waiting != 0:
            pass

# Main function
def main():
    # Declare global variables
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
        print 'Device not found'
        return
    
    # Open COM ports
    ports = []
    for c in coms:
        p = serial.Serial(c)
        p.flushInput()
        p.flushOutput()
        ports.append(p)
    
    # Switch to SiRF mode
    print 'Switching to SiRF mode...'
    for p in ports:
        portWrite(p, '$PSRF100,0,115200,8,1,0*04\r\n')
    
    # Close ports
    for p in ports:
        p.close()

if __name__ == '__main__':
    main()

