# Import libraries
import argparse

# Get arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('file',
                        action  = 'store',
                        help    = 'Data file to parse')
    return parser.parse_args()

# Main function
def main():
    args = getArguments()
    seq = ['1c', '40', '1e', '29', '43', '04', '02', '43', '07', '5d', '33']
    file = open(args.file, 'r')
    n = 0
    idx = -1
    for line in file:
        n = n + 1
        arr = line.split(' ')
        mid = arr[4]
        if idx == -1:
            if mid not in seq:
                continue
            idx = seq.index(mid)
            continue
        try:
            i = seq.index(mid)
            if i == 4 and seq[idx] == '02':
                i = 7
            if i == idx:
                continue
            if i == idx + 1:
                idx = i
                continue
            if i == 0 and idx == len(seq) - 1:
                idx = i
                continue
            if i == 3 and idx == len(seq) - 1:
                idx = i
                continue
            print n
            raw_input()
        except:
            if mid == '0b':
                continue
            if mid == '0d':
                continue
            if mid == '38' and seq[idx] == '5d':
                continue
            if mid == '38' and seq[idx] == '33':
                continue
            if mid == '5c' and seq[idx] == '40':
                continue
            if mid == 'e1' and seq[idx] == '33':
                continue
            print n
            raw_input()
    file.close()

if __name__ == '__main__':
    main()

