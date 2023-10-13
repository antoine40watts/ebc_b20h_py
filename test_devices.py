#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import signal

from ebc_b20h import EBC_B20H
# from q2_charger import Q2Charger


def signal_handler(sig, frame):
    print("Ctrl+C received. Exiting gracefully.")
    # Add cleanup or additional exit logic here if needed
    print("stopping")
    discharger.stop()
    print("disconnecting")
    discharger.disconnect()
    print("destroying")
    discharger.destroy()
    sys.exit(0)


if __name__ == "__main__":
    global discharger

    signal.signal(signal.SIGINT, signal_handler)

    print("Initializing EBC-B20H")
    discharger = EBC_B20H()
    discharger.debug = True
    discharger.logfile = None

    print("Connecting")
    discharger.connect()

    print("start monitoring")
    assert discharger.is_monitoring == False
    discharger.start_monitoring("test_log_device.txt", raw=True)
    assert discharger.is_monitoring == True

    print("IDLE for 6 seconds")
    time.sleep(6)

    # print("Disconnecting")
    # discharger.disconnect()
    # time.sleep(6)

    print("Discharging 2V @ 10Amps from connected battery")
    current_voltage = discharger.voltage
    print(f"{current_voltage=}")
    discharger.discharge(10, (current_voltage - 4)*10)

    time.sleep(6)

    while discharger.current > 0.1:
        print("current", discharger.current, " volt", discharger.voltage)
        time.sleep(2)
    
    discharger.stop()
    discharger.stop_monitoring()
    discharger.disconnect()
    discharger.destroy()


    # print("Initializing Q2-Charger")
    # charger = Q2Charger()
