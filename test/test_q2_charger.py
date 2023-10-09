#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from array import array
import time
import os.path
from q2_charger import Q2Charger


class FakeCanBus():
    def __init__(self):
        self.msg = []

    def send_periodic(self, msg, period):
        print("sending periodic message:")
        print(msg)
    
    def __iter__(self):
        return self.msg


class FakeQ2Charger(Q2Charger):
    def __init__(self):
        self.is_charging = False
        self.bus = FakeCanBus()
        self.buffer = []
        self.monitoring = False
        self.monitoring_data = []


def test_build_message():
    test_cases = []
    pass
