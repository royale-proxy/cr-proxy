#!/usr/bin/python

"""Varint encoder/decoder

varints are a common encoding for variable length integer data, used in
libraries such as sqlite, protobuf, v8, and more.

Here's a quick and dirty module to help avoid reimplementing the same thing
over and over again.
"""

# byte-oriented StringIO was moved to io.BytesIO in py3k
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

import sys
import binascii

if sys.version > '3':
    def _byte(b):
        return bytes((b, ))
else:
    def _byte(b):
        return chr(b)

def sevenBitRotateLeft(byte):
    n = int.from_bytes(byte, byteorder='big')
    seventh = (n & 0x40) >> 6 # save 7th bit
    msb = (n & 0x80) >> 7 # save msb     
    n = n << 1 # rotate to the left 
    n = n & ~(0x181) # clear 8th and 1st bit and 9th if any
    n = n | (msb << 7) | (seventh) # insert msb and 6th back in
    return bytes([n])

def sevenBitRotateRight(byte): 
    n = int.from_bytes(byte, byteorder='big')
    lsb = n & 0x1 # save lsb
    msb = (n & 0x80) >> 7 # save msb
    n = n >> 1 # rotate to the right 
    n = n & ~(0xC0) # clear 7th and 6th bit
    n = n | (msb << 7) | (lsb << 6) # insert msb and lsb back in
    return bytes([n])
 
def encode(number, isRr):
    """Pack `number` into varint bytes"""
    buf = b''
    while True:
        towrite = number & 0x7f
        number >>= 7
        if number:
            tmp = _byte(towrite | 0x80)
            if isRr and not buf:
                tmp = sevenBitRotateRight(tmp)
            buf += tmp
        else:
            buf += _byte(towrite)
            break
    return buf

def decode_stream(stream, isRr):
    """Read a varint from `stream`"""
    shift = 0
    result = 0
    while True:
        byte = _read_one(stream)
        if isRr and shift == 0:
            byte = sevenBitRotateLeft(byte)
        i = ord(byte)
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break

    return result

def decode_bytes(buf, isRr):
    """Read a varint from from `buf` bytes"""
    return decode_stream(BytesIO(buf), isRr)


def _read_one(stream):
    """Read a byte from the file (as an integer)

    raises EOFError if the stream ends while reading bytes.
    """
    c = stream.read(1)
    if c == '':
        raise EOFError("Unexpected EOF while reading bytes")
    return c

def decimalToHex(int32):
    sint32 = (int32 << 1) ^ (int32 >> 31)

    int32Bytes = encode(int32, False)
    sint32Bytes = encode(sint32, False)
    print ("int32={} bytes={}".format(int32, binascii.hexlify(int32Bytes)))
    print ("sint32={} bytes={}".format(sint32, binascii.hexlify(sint32Bytes)))    
    rrsint32Bytes = encode(sint32, True)
    print ("rrsint32={} bytes={}".format(sint32, binascii.hexlify(rrsint32Bytes)))
    
def hexToDecimal(hexStr):
    decBytes = binascii.unhexlify(hexStr)
    n = decode_bytes(decBytes, False)
    rrn = decode_bytes(decBytes, True)
    print ("int32={}".format(n))
    sint32 = (((n) >> 1) ^ (-((n) & 1)))
    print ("sint32={}".format(sint32))
    rrsint32 = (((rrn) >> 1) ^ (-((rrn) & 1)))
    print ("rrsint32={}".format(rrsint32))
    
def printHelp():
    print("""
    varint.py <decimal>
        Outputs hex encoded byte values of the decimal as required by int32, 
        sint32, and rrsint32 
        
    varint.py 0x<hex string>
        Outputs decimal values decoded by int32, sint32, and rrsint32 
    """)

def main():
    if len(sys.argv) < 2:
        printHelp()
        exit()
        
    arg = sys.argv[1];
    if (arg.startswith("0x")):
        hexToDecimal(arg[2:])
    else:
        int32 = int(arg)
        decimalToHex(int32)
    
if __name__ == "__main__":
    main()
