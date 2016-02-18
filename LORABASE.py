#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Geschreven door Edwin van den Oetelaar, all rights reserved
# python 3.4
# proof of concept, one module on USB0 and another on USB1
# put devices in P2P mode and push data from one to another
# this works

import serial
from time import sleep


class LORABASE(object):
    # some baseclass for my rx an tx objects
    _cmd_no_mac = [
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
        'mac pause'
    ]

    def connect_module(self, s=None):
        # connect module (on serial s)
        # return version number or None on fail
        # pre:  s is open serial port
        assert (s is not None)

        rv = None
        cnt = 5

        while cnt:
            s.send_break(duration=0.25)  # send break, pull TX low
            s.write(b'U')  # send 0x55 for autobaud
            sleep(0.1)
            s.write(b'sys get ver\r\n')
            r = s.readline()
            # print(r)
            if len(r) and r.startswith(b'RN2483'):
                rv = r
                break
            cnt -= 1
        return rv

    def __init__(self, port=None):
        self._firmware = None
        assert port is not None, "port must be given, name of serial device"

        try:
            self._ptx = serial.Serial(port=port, baudrate=57600, timeout=2.0, write_timeout=2.0)
        except serial.SerialException as sex:
            raise IOError(sex)

        m = self.connect_module(self._ptx)  # connect and sync with module
        if m:
            self._firmware = m
            print("Success : {m}".format(m=m))
        else:
            raise IOError('Module not talking to me')

        for m in self._cmd_no_mac:
                print('>> {m}'.format(m=m))
                self._ptx.write(m.encode())
                self._ptx.write(b'\r\n')
                r = self._ptx.readline()
                if len(r):
                    print('<< {r}'.format(r=r[:-2]))
                else:
                    print('<< no response')

    @property
    def serialport(self):
        # exposing the port
        return self._ptx

    @property
    def firmware(self):
        return self._firmware

    def setup(self):
        raise ("must me implemented in subclass")
