#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from array import array
import time
import os.path
from ebc_b20h import EBC_B20H


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
        return data

    def ctrl_transfer(self, reqtype, req, val, idx, data_size):
        print("[ctrl_transfer]", reqtype, req, val, idx, data_size)
        return



class FakeEBC_B20H(EBC_B20H):
    def __init__(self):
        self.buffer = []
        self.monitoring = False
        self.monitoring_data = []
        self.dev = FakeUSBDevice()


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


def test_encode_current():
    test_cases = [
        (0.1, (0x0, 0x0a)),
        (0.11, (0x0, 0x0b)),
        (0.5, (0x0, 0x32)),
        (12.0, (0x05, 0x0)),
    ]
    for c, result in test_cases:
        assert EBC_B20H.encode_current(c) == result


def test_log():
    print()
    dev = FakeEBC_B20H()
    dev.connect()
    dev.discharge(current=1.0, vcutoff=2.5)

    print(dev.recieve())
    
    dev.start_monitoring("test_log.txt")
    time.sleep(100)
    dev.stop_monitoring()