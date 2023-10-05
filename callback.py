#!/usr/bin/python3
# -*- coding: utf-8 -*

import serial
import struct
import send_data
import pigpio
import binascii

import time

def reflect_data(x, width):
    if width == 8:
        x = ((x & 0x55) << 1) | ((x & 0xAA) >> 1)
        x = ((x & 0x33) << 2) | ((x & 0xCC) >> 2)
        x = ((x & 0x0F) << 4) | ((x & 0xF0) >> 4)
    else:
        raise ValueError('Unsupported width')
    return x

def crc_poly(data, n, poly, crc=0, ref_in=False, ref_out=False, xor_out=0):
    g = 1 << n | poly
    for d in data:
        if ref_in:
            d = reflect_data(d, 8)
        crc ^= d << (n - 8)
        for _ in range(8):
            crc <<= 1
            if crc & (1 << n):
                crc ^= g
    if ref_out:
        crc = reflect_data(crc, n)
    return crc ^ xor_out

ser = serial.Serial(
      port = "/dev/ttyUSB0",
      baudrate = 19200,
      parity = serial.PARITY_NONE,
      bytesize = serial.EIGHTBITS,
      stopbits = serial.STOPBITS_ONE,
      #timeout = None,
      #xonxoff = 0,
      #rtscts = 0,
      )

tmp = 0
s_code = b"\x02"
s_ID = b"\x00"
s_com = b"\x0f"

data2= s_code + s_ID + s_com

#print(data2)

crc = crc_poly(data2, 8, 0x85)
ccrc = binascii.unhexlify(format(crc,'x'))
#print (ccrc)

pi=pigpio.pi()

while True:
      if ser.in_waiting > 0:
            recv_data = ser.read(1)
            if(tmp==0 and recv_data==b'\x02'):
                print("packet start!")
                tmp=1

            elif(tmp==1 and recv_data==s_code):
                print("s_code OK:" + recv_data.hex())
                tmp=2

            elif(tmp==2 and recv_data==s_ID):
                print("s_ID OK:" + recv_data.hex())
                tmp=3

            elif(tmp==3 and recv_data==s_com):
                print("sent packet!:" + recv_data.hex())
                tmp=4

            elif(tmp==4 and recv_data == ccrc):
                return_data = send_data.senser_get(ser,pi)
                print("call sub")
                if return_data == 0: #error
                    num = 0
                    while (return_data == 0 and num <= 10):
                        return_data = send_data.senser_get(ser,pi)
                        print("call sub")
                        num = num + 1
                        time.sleep(0.05)
                tmp=5

            #elif(tmp==5 and recv_data==b'\x03'):
            elif(tmp==5):
                print("packet end!")
                tmp=0

            else :
                print(tmp)
                print("packet error")
                tmp=0
