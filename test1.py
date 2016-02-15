#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Geschreven door Edwin van den Oetelaar, all rights reserved
# python 3.4
# proof of concept, one module on USB0 and another on USB1
# put devices in P2P mode and push data from one to another
# this works

import serial


if __name__ == '__main__':
    prx = serial.Serial(port='/dev/ttyUSB0', baudrate=57600, timeout=2.0, write_timeout=2.0)
    ptx = serial.Serial(port='/dev/ttyUSB1', baudrate=57600, timeout=2.0, write_timeout=2.0)

    cmdsrx = [
        'sys get ver',
        'radio set mod lora',
        'radio set freq 868000000',
        'radio set pwr 14',
        'radio set sf sf12',
        'radio set afcbw 125',
        'radio set rxbw 250',
        'radio set fdev 5000',
        'radio set prlen 8',
        'radio set crc on',
        'radio set cr 4/8',
        'radio set wdt 0',
        'radio set sync 12',
        'radio set bw 250',
        'mac pause',
        'radio rx 0'
    ]

    cmdstx = [
        'sys get ver',
        'radio set mod lora',
        'radio set freq 868000000',
        'radio set pwr 14',
        'radio set sf sf12',
        'radio set afcbw 125',
        'radio set rxbw 250',
        'radio set fdev 5000',
        'radio set prlen 8',
        'radio set crc on',
        'radio set cr 4/8',
        'radio set wdt 0',
        'radio set sync 12',
        'radio set bw 250',
        'mac pause',
    ]

    for m in cmdsrx:
        print('>> {m}'.format(m=m))
        prx.write(m.encode())
        prx.write(b'\r\n')
        r = prx.readline()
        print('<< {r}'.format(r=r[:-2]))

    for m in cmdstx:
        print('>> {m}'.format(m=m))
        ptx.write(m.encode())
        ptx.write(b'\r\n')
        r = ptx.readline()
        print('<< {r}'.format(r=r[:-2]))

    message = b'ABCDEFGHIJKLMNOPQ het werkt'
    i = 0
    msglen = len(message)
    tx_allow = True
    while True:
        if prx.readable():
            r = prx.readline()
            if len(r):
                print('<< prx {r}'.format(r=r[:-2]))
                s = r.decode()
                if s.startswith('radio_rx'):
                    # we got some data
                    l = len(s)
                    # bytearray.fromhex("7061756c").decode()
                    h = s[10:][:-2]

                    ba = bytearray.fromhex(h)
                    st = ba.decode()
                    print('got string {st}'.format(st=st))
                    for b in ba:
                        print('got char {b}'.format(b=b))
                    # tell the radio to get more data
                    prx.write(b'radio rx 0\r\n')

        if ptx.readable():
            r = ptx.readline()
            if len(r):
                print('<< ptx {r}'.format(r=r[:-2]))
                s = r.decode()
                if s.startswith('radio_tx_ok'):
                    # TX is done, we can send more data now
                    tx_allow = True

        if tx_allow:
            # write something in TX
            if i < msglen:
                c = hex(message[i])[2:]  # strip 0x
                m = 'radio tx {xx}'.format(xx=c)
                print('>> ptx {m}'.format(m=m))
                ptx.write(m.encode())
                ptx.write(b'\r\n')
                i += 1
                tx_allow = False
            else:
                break
