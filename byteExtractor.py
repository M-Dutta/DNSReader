import argparse
import binascii
import struct
import binascii
files ='test.bin'

parser = argparse.ArgumentParser()
parser.add_argument('--f',type=str, nargs='?')
args = parser.parse_args()
if (args.f):
    files = args.f

def extractb(fileName):
    bytelist =[]
    with open(fileName,'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                break
            byte = binascii.hexlify(byte)
            bytelist.append(byte)
    f.close()
    return bytelist

def extract(fileName):
    bytelist =[]
    with open(fileName,'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                break
            byte = binascii.hexlify(byte)
            byte =str(byte)[2:4]
            bytelist.append(byte)
    f.close()
    return bytelist

bt =extract(files)
print(bt)
