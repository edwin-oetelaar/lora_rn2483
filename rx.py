#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Geschreven door Edwin van den Oetelaar, all rights reserved
# python 3.4
# proof of concept, one module on USB0 and another on USB1
# put devices in P2P mode and push data from one to another
# this works

import serial
from time import sleep
import datetime
from LORABASE import LORABASE


class LoRaRx(LORABASE):
    def __init__(self, port=None):
        super().__init__(port)

    def receive(self):

        # tell the radio to get more data
        self._ptx.write(b'radio rx 0\r\n')

        while True:
            # wait until we RX anything
            if self._ptx.readable():
                r = self._ptx.readline()

                if len(r):
                    # print('<< prx {r}'.format(r=r[:-2]))
                    s = r.decode()
                    if s.startswith('radio_rx'):
                        print(datetime.datetime.utcnow())
                        # we got some data
                        l = len(s)
                        # bytearray.fromhex("7061756c").decode()
                        h = s[10:][:-2]

                        ba = bytearray.fromhex(h)
                        st = ba.decode()
                        print('got string {st}'.format(st=st))
                        for b in ba:
                            print('got char {b}'.format(b=b))

                        break

                    elif s.startswith('busy'):
                        print('unexpected, the receiver is still busy')
                    elif s.startswith('invalid_param'):
                        print('unexpected protocol param error')
                    elif s.startswith('ok'):
                        pass
                        # print('all good')
                    else:
                        print('really unexpected stuff')


if __name__ == '__main__':

    try:
        rx = LoRaRx(port='/dev/ttyUSB0')
    except IOError as ioex:
        # problem
        print('could not connect to module')
        exit(1)
    else:
        print('Module connected : {x}'.format(x=rx.firmware))

    # receive until hell freezes over
    while True:
        rx.receive()
