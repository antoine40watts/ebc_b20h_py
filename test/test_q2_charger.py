#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from array import array
import time
import os.path
from q2_charger import Q2Charger


class FakeQ2Charger(Q2Charger):
    def __init__(self):
        self.buffer = []
        self.monitoring = False
        self.monitoring_data = []
        self.bus = None


def test_build_message():
    test_cases = []
    pass
