#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from .ebc_b20h import EBC_B20H
from .q2_charger import Q2Charger


if __name__ == "__main__":
    print("Initializing EBC-B20H")
    discharger = EBC_B20H()
    discharger.debug = True
    discharger.logfile = None
    discharger.find_device()
    discharger.connect()

    discharger.start_monitoring("test_log_device.txt", raw=True)

    print("Discharging 2V @ 10Amps from connected battery")
    current_voltage = discharger.voltage
    discharger.discharge(10, current_voltage - 2)

    time.sleep(5)
    while discharger.current > 0.1:
        time.sleep(2)
    discharger.stop_monitoring()


    # print("Initializing Q2-Charger")
    # charger = Q2Charger()

    discharger.disconnect()
    discharger.destroy()