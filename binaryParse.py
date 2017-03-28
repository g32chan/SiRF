# Import libraries
import argparse
import os

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action = 'store',
                        help   = 'Data file to parse')
    return parser.parse_args()

# Main function
def main():
    # Get arguments
    args = getArguments()
    
    # Open files
    f1 = open(args.file, 'rb')
    f2 = open('parsed_' + args.file, 'ab')
    
    # Find start of first message
    while True:
        data = f1.read(2)
        if data != 'a0':
            continue
        prev = data
        data = f1.read(2)
        if data != 'a2':
            continue
        f2.write(prev + ' ' + data + ' ')
        f2.flush()
        os.fsync(f2)
        break
    
    while data != '':
        data = f1.read(2)
        f2.write(data + ' ')
        if data != 'b0':
            continue
        data = f1.read(2)
        f2.write(data + ' ')
        if data != 'b3':
            continue
        data = f1.read(2)
        if data == 'a0':
            f2.write('\r\n')
        f2.write(data + ' ')
    
    # Close files
    f1.close()
    f2.close()
    
    # Cleanup
    os.remove(args.file)
    os.rename('parsed_' + args.file, args.file)

if __name__ == '__main__':
    main()

