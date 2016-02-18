#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Geschreven door Edwin van den Oetelaar, all rights reserved
# python 3.4
# proof of concept, one module on USB0 and another on USB1
# put devices in P2P mode and push data from one to another
# this works

import serial
from time import sleep

from LORABASE import LORABASE


class LoRaTx(LORABASE):
    def __init__(self, port=None):
        super().__init__(port)

    def transmit(self,data=None):
        assert data is not None, "Can not send None to other side"
        i = 0
        msglen = len(data)
        tx_allow = True
        while True:
            if self._ptx.readable():
                r = self._ptx.readline()
                if len(r):
                    print('<< tx {r}'.format(r=r[:-2]))
                    s = r.decode()
                    if s.startswith('radio_tx_ok'):
                        print('module confirmed Tx by radio')
                        # TX is done, we can send more data now
                        tx_allow = True
                    elif s.startswith('ok'):
                        print('module accepted Tx command')
                    else:
                        print("module reponse unexpected")

            if tx_allow:
                # write something in TX
                if i < msglen:
                    c = hex(data[i])[2:]  # strip 0x
                    m = 'radio tx {xx}'.format(xx=c)
                    print('>> _ptx {m}'.format(m=m))
                    self._ptx.write(m.encode())
                    self._ptx.write(b'\r\n')
                    i += 1
                    tx_allow = False
                else:
                    break


if __name__ == '__main__':

    try:
        tx = LoRaTx(port='/dev/ttyUSB1')
    except IOError as ioex:
        # problem
        print('could not connect to module')
        exit(1)
    else:
        print('Module connected : {x}'.format(x=tx.firmware))

    data = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ Edwin says : het werkt'

    # transmit until hell freezes over
    while True:
        tx.transmit(data)
