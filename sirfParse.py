# Import libraries
import argparse
import binascii
import struct

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action = 'store',
                        help   = 'Data file to parse')
    parser.add_argument('-n', '--nav',
                        action = 'store_true',
                        help   = 'Process navigation data (MID 2)')
    parser.add_argument('-c', '--clk',
                        action = 'store_true',
                        help   = 'Process clock data (MID 7)')
    parser.add_argument('-v', '--vis',
                        action = 'store_true',
                        help   = 'Process visibility data (MID 13)')
    parser.add_argument('-r', '--raw',
                        action = 'store_true',
                        help   = 'Process raw data (MID 28)')
    parser.add_argument('-s', '--sv',
                        action = 'store_true',
                        help   = 'Process SV state date (MID 30)')
    parser.add_argument('-g', '--geo',
                        action = 'store_true',
                        help   = 'Process geodetic data (MID 41)')
    return parser.parse_args()

# Double precision float conversion
def convertDouble(str):
    n = len(str) / 2
    return struct.unpack('>d', binascii.unhexlify(str[n:] + str[:n]))[0]

# Single precision float conversion
def convertSingle(str):
    return struct.unpack('>f', binascii.unhexlify(str))[0]

# Signed integer conversion
def convertSigned(str):
    n = int(str, 16)
    if n > 2 ** (len(str) * 4 - 1):
        return n - 2 ** (len(str) * 4)
    else:
        return n

# Main function
def main():
    # Get arguments
    args = getArguments()
    
    # Open files and write headers
    data = open(args.file, 'r')
    if args.raw:
        fraw = open(args.file.split('.')[0] + '_results.csv', 'wb')
        fraw.write('Channel,Satellite,GPS Time,Pseudorange,Carrier Frequency,'
                'Carrier Phase,CNR 1,CNR 2,CNR 3,CNR 4,CNR 5,CNR 6,CNR 7,CNR 8,'
                'CNR 9,CNR 10\r\n')
    if args.clk:
        fclk = open(args.file.split('.')[0] + '_clock.csv', 'wb')
        fclk.write('GPS Week,ToW,SVs,Clock Drift,Clock Bias,Est. GPS Time\r\n')
    if args.nav:
        fnav = open(args.file.split('.')[0] + '_nav.csv', 'wb')
        fnav.write('X,Y,Z,Vx,Vy,Vz,Mode1,GPS Week,ToW\r\n')
    if args.geo:
        fgeo = open(args.file.split('.')[0] + '_geo.csv', 'wb')
        fgeo.write('GPS Week,ToW,Lat,Lon,Alt Ellip,Alt MSL\r\n')
    if args.sv:
        fsv = open(args.file.split('.')[0] + '_sv.csv', 'wb')
        fsv.write('Satellite,GPS Time,X,Y,Z,Vx,Vy,Vz,Clock Bias\r\n')
    if args.vis:
        fvis = open(args.file.split('.')[0] + '_visible.csv', 'wb')
        fvis.write('Ch1 ID,Ch1 Az,Ch1 El,'
                   'Ch2 ID,Ch2 Az,Ch2 El,'
                   'Ch3 ID,Ch3 Az,Ch3 El,'
                   'Ch4 ID,Ch4 Az,Ch4 El,'
                   'Ch5 ID,Ch5 Az,Ch5 El,'
                   'Ch6 ID,Ch6 Az,Ch6 El,'
                   'Ch7 ID,Ch7 Az,Ch7 El,'
                   'Ch8 ID,Ch8 Az,Ch8 El,'
                   'Ch9 ID,Ch9 Az,Ch9 El,'
                   'Ch10 ID,Ch10 Az,Ch10 El,'
                   'Ch11 ID,Ch11 Az,Ch11 El,'
                   'Ch12 ID,Ch12 Az,Ch12 El,'
                   'Ch13 ID,Ch13 Az,Ch13 El,'
                   'Ch14 ID,Ch14 Az,Ch14 El,'
                   'Ch15 ID,Ch15 Az,Ch15 El,'
                   'Ch16 ID,Ch16 Az,Ch16 El,'
                   'Ch17 ID,Ch17 Az,Ch17 El,'
                   'Ch18 ID,Ch18 Az,Ch18 El,'
                   'Ch19 ID,Ch19 Az,Ch19 El,'
                   'Ch20 ID,Ch20 Az,Ch20 El\r\n')
    
    # Parse data
    for line in data:
        str = line.strip().replace(' ', '')
        if args.raw and str[6:8] == '38' and str[8:10] == '1c' and len(str) == 128:
            fraw.write('{},'.format(int(str[10:12], 16)))
            fraw.write('{},'.format(int(str[20:22], 16)))
            fraw.write('{},'.format(convertDouble(str[22:38])))
            fraw.write('{},'.format(convertDouble(str[38:54])))
            fraw.write('{},'.format(convertSingle(str[54:62])))
            fraw.write('{},'.format(convertDouble(str[62:78])))
            fraw.write('{},'.format(int(str[84:86], 16)))
            fraw.write('{},'.format(int(str[86:88], 16)))
            fraw.write('{},'.format(int(str[88:90], 16)))
            fraw.write('{},'.format(int(str[90:92], 16)))
            fraw.write('{},'.format(int(str[92:94], 16)))
            fraw.write('{},'.format(int(str[94:96], 16)))
            fraw.write('{},'.format(int(str[96:98], 16)))
            fraw.write('{},'.format(int(str[98:100], 16)))
            fraw.write('{},'.format(int(str[100:102], 16)))
            fraw.write('{}\r\n'.format(int(str[102:104], 16)))
        if args.clk and str[6:8] == '14' and str[8:10] == '07' and len(str) == 56:
            fclk.write('{},'.format(int(str[10:14], 16)))
            fclk.write('{},'.format(int(str[14:22], 16)))
            fclk.write('{},'.format(int(str[22:24], 16)))
            fclk.write('{},'.format(int(str[24:32], 16)))
            fclk.write('{},'.format(int(str[32:40], 16)))
            fclk.write('{}\r\n'.format(int(str[40:48], 16)))
        if args.nav and str[6:8] == '2f' and str[8:10] == '02' and len(str) == 110:
            fnav.write('{},'.format(convertSigned(str[10:18])))
            fnav.write('{},'.format(convertSigned(str[18:26])))
            fnav.write('{},'.format(convertSigned(str[26:34])))
            fnav.write('{},'.format(convertSigned(str[34:38])))
            fnav.write('{},'.format(convertSigned(str[38:42])))
            fnav.write('{},'.format(convertSigned(str[42:46])))
            fnav.write('{},'.format(int(str[46:48], 16)))
            fnav.write('{},'.format(int(str[52:56], 16)))
            fnav.write('{}\r\n'.format(int(str[56:64], 16)))
        if args.geo and str[6:8] == '5b' and str[8:10] == '29' and len(str) == 198:
            fgeo.write('{},'.format(int(str[18:22], 16)))
            fgeo.write('{},'.format(int(str[22:30], 16)))
            fgeo.write('{},'.format(convertSigned(str[54:62])))
            fgeo.write('{},'.format(convertSigned(str[62:70])))
            fgeo.write('{},'.format(convertSigned(str[70:78])))
            fgeo.write('{}\r\n'.format(convertSigned(str[78:86])))
        if args.sv and str[6:8] == '53' and str[8:10] == '1e' and len(str) == 182:
            fsv.write('{},'.format(int(str[10:12], 16)))
            fsv.write('{},'.format(convertDouble(str[12:28])))
            fsv.write('{},'.format(convertDouble(str[28:44])))
            fsv.write('{},'.format(convertDouble(str[44:60])))
            fsv.write('{},'.format(convertDouble(str[60:76])))
            fsv.write('{},'.format(convertDouble(str[76:92])))
            fsv.write('{},'.format(convertDouble(str[92:108])))
            fsv.write('{},'.format(convertDouble(str[108:124])))
            fsv.write('{}\r\n'.format(convertDouble(str[124:140])))
        if args.vis and str[8:10] == '0d':
            num = int(str[10:12], 16)
            if len(str) == (5*num+2)*2+16:
                for i in range(num):
                    fvis.write('{},'.format(int(str[10*i+12:10*i+14], 16)))
                    fvis.write('{},'.format(convertSigned(str[10*i+14:10*i+18])))
                    fvis.write('{},'.format(convertSigned(str[10*i+18:10*i+22])))
                fvis.write('\r\n')
    
    # Close files
    if args.raw:
        fraw.close()
    if args.clk:
        fclk.close()
    if args.nav:
        fnav.close()
    if args.geo:
        fgeo.close()
    if args.sv:
        fsv.close()
    if args.vis:
        fvis.close()
    data.close()

if __name__ == '__main__':
    main()

