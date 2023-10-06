#!/usr/bin/python3
# -*- coding: utf-8 -*

import serial
import time
import pigpio

import bme280
import compute_crc8_atm

THERMO_HIGEST = 90
THERMO_HIGT = 85
THERMO_LOW = 70

ser_v = serial.Serial('/dev/ttyUSB0', 19200, timeout=None)

stop_times = 0.77
datagram = []

def senser_get(ser,pi):

    d_ed = "big"

    s_code = b'\x02'
    s_ID = b'\x00'
    addr = 0x0a

    try:
        h = pi.i2c_open(1,addr)
        pi.i2c_write_device(h, [0x4d])
        time.sleep(stop_times)
        count, result = pi.i2c_read_device(h,2051)
        time.sleep(stop_times)
        pi.i2c_close(h)
    except:
        count = -80

#    print(count)
#    print(result)

    if count <= 0: #device_error
        return (0)
    else:
        readbuff = bytes(result)

        s_bit = b"\x02"

        ser.write(s_bit)

        ser.write(s_code)
        ser.write(s_ID)
        #print(s_code)
        #print(s_ID)
        #datagram.append(s_code)
        #datagram.append(s_ID)

        tmp_termo = 0

        for i in range(1025):
            ttmp = readbuff[i*2]
            msg = ttmp.to_bytes(1,d_ed)
            ser.write(msg)
            #datagram.append(msg)
            #time.sleep(0.01) #2023.9.13

            tttmp = readbuff[i*2+1]
            msg = tttmp.to_bytes(1,d_ed)
            ser.write(msg)
            #datagram.append(msg)

            if(tmp_termo <= (256 * tttmp + ttmp)/10):
                tmp_termo = (256 * tttmp + ttmp)/10

        tPEC = readbuff[2050]
        msg = tPEC.to_bytes(1,d_ed)
        ser.write(msg)
        #datagram.append(msg)

        #add 2023/08/23
        if (tmp_termo >= THERMO_HIGT):
            msg = b"\x02"
        elif (tmp_termo >= THERMO_LOW):
            msg = b"\x01"
        else:
            msg = b"\x00"
        #print(tmp_termo)
        #print(msg)
        ser.write(msg)
        datagram.append(msg) #:1

        bme280.init_bme280()
        bme280.read_compensate()
        tmp,prs,hum = bme280.read_data()

        tmp = round(tmp,1)
        tmp = tmp * 10
        ttmp = int(tmp % 256)
        tttmp = int(tmp) >> 8
        #tmp_termo = (256 * tttmp + ttmp)/10
        #print(tmp_termo)

        msg = ttmp.to_bytes(1,d_ed)
        ser.write(msg)
        datagram.append(msg) #:2

        msg = tttmp.to_bytes(1,d_ed)
        ser.write(msg)
        datagram.append(msg) #:3

        #crc
        byte_datagram = b''.join(datagram)
        #print(byte_datagram)
        resurt = compute_crc8_atm.compute_crc8_atm(byte_datagram, initial_value=0)
        msg = resurt.to_bytes(1,d_ed)
        ser.write(msg)
        #print(msg)

        #end
        msg = b"\x03"
        ser.write(msg)

        return(1)

if __name__ == "__main__":

    pi2 = pigpio.pi()
    return_data = senser_get(ser_v,pi2)
    if return_data == 0:
        num = 0
        while return_data == 0 and num <= 3:
            return_data = senser_get(ser_v,pi2)
            num = num + 1
    pi2.stop()
