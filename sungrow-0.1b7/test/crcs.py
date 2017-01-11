
from math import ceil, log
import struct

import CrcMoose

def bits(i, num_bits=None):
    if num_bits is None:
        num_bits = int(ceil(log(i, 2)))
    return [(i >> shift) & 1 for shift in range(num_bits)]

def poly_from_hex(i):
    b = bits(i, 16)
    ints = [16]
    ints += [j for j in range(15, -1, -1) if b[j]]
    return tuple(ints)

## poly, init, xorout
hexes = {'CRC-16/IBM' : (0x8005, 0x0000, 0x0000),
         'CRC-16/AUG-CCITT' : (0x1021, 0x1d0f, 0x0000),
         'CRC-16/CCITT-FALSE' : (0x1021, 0xffff, 0x0000),
         'CRC-16/DDS-110' : (0x8005, 0x800D, 0x0000),
         'CRC-16/DECT-R': (0x0589, 0x0000, 0x0001),
         'CRC-16/DECT-X': (0x0589, 0x0000, 0x0000),
         'CRC-16/DNP' : (0x3d65, 0x0000, 0xffff),
         'CRC-16/GENIBUS' : (0x1021, 0xffff, 0xffff),
         'CRC-16-IBM' : (0x8005, 0x0000, 0xffff),
         'CRC-16/MCRF4XX' : (0x1021, 0xffff, 0x0000),
         'CRC-16/RIELLO' : (0x1021, 0xb2aa, 0x0000),
         'CRC-16/T10-DIF' : (0x8bb7, 0x0000, 0x0000),
         'CRC-16/TELEDISK' : (0xa097, 0x0000, 0x0000),
         'CRC-16/TMS37157' : (0x1021, 0x89ec, 0x0000),
         'CRC-16/USB' : (0x8005, 0xffff, 0xffff),
         'CRC-A' : (0x1021, 0xc6c6, 0x0000),
         'KERMIT' : (0x1021, 0x0000, 0x0000),
         'MODBUS' : (0x8005, 0xffff, 0x0000),
         'X-25' : (0x1021, 0xffff, 0xffff),
##         'XMODEM' : (0x1021, 0x0000, 0x0000),
}

## "check" field is the checksum for the ASCII string "123456789"

message = '\x01\x03\x07\x00\x01\x00\x00\x00\x00\x00\x00'
name = 'MODBUS'
poly, init, xorout = hexes[name]
poly = poly_from_hex(poly)
assert poly == (16, 15, 2, 0)
alg = CrcMoose.CrcAlgorithm(name='CRC-Sungrow',
                            width=16,
                            polynomial=poly,
                            seed=init,
                            lsbFirst=True,
                            xorMask=xorout)
digest = int(alg.calcString(message))
assert digest == 59332
## hex (little-endian)
assert struct.pack('<H', digest) == '\xc4\xe7'
