#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from array import array
import time
import os.path
import logging
from random import randrange
from ebc_b20h import EBC_B20H
import asyncio


class FakeUSBDevice():
    def __init__(self):
        curdir = os.path.split(os.path.abspath(__file__))[0]
        print(curdir)
        with open(os.path.join(curdir, "log.txt"), 'r') as f:
            self.log = [list(map(int, line.split())) for line in f.readlines()]
        self.log_i = 0

    def write(self, addr, data, timeout):
        formated = ' '.join([f'{b:3}' for b in data])
        print("[write]", formated)
        #print(data)
        return
    
    def read(self, addr, size, timeout):
        data = array('h')
        for b in self.log[self.log_i]:
            data.append(b)
        self.log_i += 1
        if self.log_i >= len(self.log):
            self.log_i = 0
        return data

    def ctrl_transfer(self, reqtype, req, val, idx, data_size):
        print("[ctrl_transfer]", reqtype, req, val, idx, data_size)
        return



class LogEBC_B20H(EBC_B20H):
    def __init__(self):
        self.buffer = []
        self.is_monitoring = False
        self.is_charging = False
        self.is_discharging = False
        self.waiting_for_status = 0
        self.dev = FakeUSBDevice()
        self.debug = False
    
    def destroy(self):
        return



class VirtEBC_B20H(EBC_B20H):
    def __init__(self):
        super().__init__()

        self.dev = FakeUSBDevice()

        self.discharge_current = 0
        self.discharge_cutoff_v = 0
        self.charge_cutoff_v = 29.4
        self.voltage = 29
    
    def find_device(self):
        return

    def destroy(self):
        return

    def charge(self, cutoff_c = 0.1):
        self.charge_cutoff_c = cutoff_c
        self.mah = 0
        return super().charge(cutoff_c)

    def discharge(self, current=1, cutoff_v=2, cont=False):
        self.discharge_current = current
        self.discharge_cutoff_v = cutoff_v
        self.mah = 0
        return super().discharge(current, cutoff_v, cont)

    def adjust(self, current, cutoff_v):
        self.discharge_current = current
        self.discharge_cutoff_v = cutoff_v
        self.is_discharging = True
        return super().adjust(current, cutoff_v)

    def stop(self):
        self.is_charging = False
        super().stop()

    def recieve(self):
        """
            Anatomy of a response:
                250  10   4  40 150 185   0 220   0   0   4  40   0 200   0   0  28  45 248
                som sta  c1  c2  v1  v2  e1  e2         dc1 dc2 dv1 dv2
            
                sta: status byte
                    10 (0x0A): discharging
                    11 (0x0B): charging
                    20 (0x14): end of discharge
                    21 (0x15): end of charge
                    100: ?
                    110: ?
                    120: ?

                c1, c2: battery discharge current
                v1, v2: battery voltage
                e1, e2: energy transfered
                dc1, dc2: user defined discharge current
                dv1, dv2: user defined min voltage
        """

        state = 0
        c1, c2 = 0, 0
        if self.is_discharging:
            state = 20 if self.voltage <= self.discharge_cutoff_v else 10
            self.voltage -= self.mah * 0.00001
            self.current = self.discharge_current
            self.mah += self.current * 10000 * 2 / 3600
            c1, c2 = EBC_B20H.encode_current(self.discharge_current)
        elif self.is_charging:
            state = 21 if self.voltage > self.charge_cutoff_v else 11
            self.voltage += self.mah * 0.00001
            self.current = 20
            self.mah += 20 * 10000 * 2 / 3600 # 20 bogo-Amps
            c1, c2 = EBC_B20H.encode_current(20)
        v1, v2 = EBC_B20H.encode_voltage(self.voltage * 10)
        e1, e2 = EBC_B20H.encode_mah(round(self.mah))
        dc1, dc2 = EBC_B20H.encode_current(self.discharge_current)
        dv1, dv2 = EBC_B20H.encode_voltage(self.discharge_cutoff_v)
        
        data = [state, c1, c2, v1, v2, e1, e2, 0, 0, dc1, dc2, dv1, dv2, 0, 0, 28]
        crc = EBC_B20H.checksum(data)

        line = [250] + data + [crc] + [248]
        
        logging.debug('<<< ' + ' '.join( [f"{str(val):>3}" for val in line] ))

        if self.debug:
            if self.logfile:
                fout = open(self.logfile, 'a')
            else:
                fout = sys.stdout
            print('<<< ' + ' '.join( [f"{str(val):>3}" for val in line] ), file=fout)
            if self.logfile:
                fout.close()
        
        return [line]



def test_checksum():
    test_cases = [
        ([0x01, 0, 0x32, 0x0C, 0x78, 0, 0], 0x47),
        ([0x01, 0, 0x32, 0x0d, 0x50, 0, 0], 0x6E),
        ([0x01, 0, 0x64, 0x0C, 0x78, 0, 0], 0x11),
        ([0x01, 0, 0x64, 0x03, 0x50, 0, 0], 0x36),
    ]
    for t, result in test_cases:
        assert EBC_B20H.checksum(t) == result


def test_encode_voltage():
    test_cases = [
        (30.0, (0x0C, 0x78)),
        (32.0, (0x0D, 0x50)),
        (8.0, (0x03, 0x50)),
        (2.0, (0x0, 0xC8)),
    ]
    for v, result in test_cases:
        assert EBC_B20H.encode_voltage(v) == result


def test_decode_voltage():
    test_cases = [
        ((67, 160), 16.24),
        ((97, 70), 23.35),
        ((105, 180), 25.38),
        ((149, 0), 29.92),
        ((155, 0), 44.32)
    ]
    for (msb, lsb), result in test_cases:
        assert EBC_B20H.decode_voltage(msb, lsb) == result


def test_encode_current():
    test_cases = [
        (0.1, (0x0, 0x0a)),
        (0.11, (0x0, 0x0b)),
        (0.5, (0x0, 0x32)),
        (12.0, (0x05, 0x0)),
    ]
    for c, result in test_cases:
        assert EBC_B20H.encode_current(c) == result


def test_encode_decode_mah():
    for _ in range(100):
        mah = randrange(0, 10000)
        msb, lsb = EBC_B20H.encode_mah(mah)
        assert mah == EBC_B20H.decode_mah(msb, lsb)
    
    for _ in range(100):
        mah = randrange(10000, 50000)
        msb, lsb = EBC_B20H.encode_mah(mah)
        assert abs(mah - EBC_B20H.decode_mah(msb, lsb)) <= 5


def test_log():
    print()
    dev = LogEBC_B20H()
    dev.connect()
    dev.discharge(current=1.0, cutoff_v=2.5)

    print(dev.recieve())
    
    dev.start_monitoring("test_log.txt")
    time.sleep(100)
    dev.stop_monitoring()


async def test_async_monitoring():
    discharger = VirtEBC_B20H()
    discharger.connect()
    discharger.discharge(2, 26)
    await asyncio.sleep(10)
    discharger.stop()
    await discharger.disconnect()