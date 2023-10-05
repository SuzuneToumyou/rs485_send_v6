#!/usr/bin/python3
# -*- coding: utf-8 -*

def compute_crc8_atm(datagram, initial_value=0):
    crc = initial_value
    for byte in datagram:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
               crc = (crc << 1) ^ 0x07 & 0xFF
            else:
               crc = (crc << 1) & 0x0FF
    crc &= 0xFF
    return crc
