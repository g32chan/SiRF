import argparse
import binascii
import struct

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action  = 'store',
                        help    = 'Data file to parse')
    return parser.parse_args()

# Double precision float conversion
def convertDouble(str):
    n = len(str) / 2
    return struct.unpack('>d', binascii.unhexlify(str[n:] + str[:n]))[0]

# Single precision float conversion
def convertSingle(str):
    return struct.unpack('>f', binascii.unhexlify(str))[0]

# Main function
def main():
    args = getArguments()
    data = open(args.file, 'r')
    f = open('results_' + args.file + '.csv', 'wb')
    f.write('Channel,Satellite,GPS Time,Pseudorange,Carrier Frequency,'
            'Carrier Phase,CNR 1,CNR 2,CNR 3,CNR 4,CNR 5,CNR 6,CNR 7,CNR 8,'
            'CNR 9,CNR 10\r\n')
    for line in data:
        str = line.strip().replace(' ', '')
        if str[6:8] == '38' and str[8:10] == '1c' and len(str) == 128:
            f.write('{},'.format(int(str[10:12], 16)))
            f.write('{},'.format(int(str[20:22], 16)))
            f.write('{},'.format(convertDouble(str[22:38])))
            f.write('{},'.format(convertDouble(str[38:54])))
            f.write('{},'.format(convertSingle(str[54:62])))
            f.write('{},'.format(convertDouble(str[62:78])))
            f.write('{},'.format(int(str[84:86], 16)))
            f.write('{},'.format(int(str[86:88], 16)))
            f.write('{},'.format(int(str[88:90], 16)))
            f.write('{},'.format(int(str[90:92], 16)))
            f.write('{},'.format(int(str[92:94], 16)))
            f.write('{},'.format(int(str[94:96], 16)))
            f.write('{},'.format(int(str[96:98], 16)))
            f.write('{},'.format(int(str[98:100], 16)))
            f.write('{},'.format(int(str[100:102], 16)))
            f.write('{}\r\n'.format(int(str[102:104], 16)))
    f.close()
    data.close()

if __name__ == '__main__':
    main()

