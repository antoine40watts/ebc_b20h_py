#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List
from time import sleep

# https://python-can.readthedocs.io
import can  # pip install python-can



class Q2Charger():
    # Deligreen Q2-1.5KWh Charger

    emit_id = 0x18FF50E5
    recv_id = 0x1806E5F4

    def __init__(self):
        self.bus = can.Bus(interface='socketcan', channel='can0')
        self.is_charging = False


    def charge(self, current, voltage):
        msg = self._build_charge_message(current, voltage)
        if self.is_charging:
            self.task.modify_data(msg)
            print("[Q2] Charging updated")
        else:
            self.task = self.bus.send_periodic(msg, 1.0)
            self.is_charging = True
            print("[Q2] Charging started")


    def stop(self):
        self.task.stop()
        self.is_charging = False
        print("[Q2] Charging stopped")
    

    def monitor(self):
        for msg in self.bus:
            if msg.arbitration_id != Q2Charger.emit_id:
                continue
            print(hex(msg.arbitration_id), msg.data)
            print(self.decode_frame(msg.data))

    
    def decode_frame(self, data: bytearray) -> dict:
        output_v = (data[0] * 255 + data[1]) / 10
        output_c = (data[2] * 255 + data[3]) / 10
        temp = data[5] - 100 # in degrees celcius
        
        # Status byte:
        #   bit0: Hardware failure
        #   bit1: Charger too hot
        #   bit2: Wrong input voltage
        #   bit3: Battery not connected or reverse polarity
        #   bit4: Communication reception timeout
        #   bit5: -
        #   bit6: -
        #   bit7: -
        status = bin(data[4])

        return {'voltage': output_v, 'current': output_c, 'temp': temp, 'status': status}


    def destroy(self):
        self.bus.stop_all_periodic_tasks()
        self.bus.shutdown()


    def _build_charge_message(self, current, voltage) -> can.Message:
        v_msb = int(voltage * 10 / 256)
        v_lsb = int(voltage * 10 - v_msb * 256)

        c_msb = int(current * 10 / 256)
        c_lsb = int(current * 10 - c_msb * 256)

        msg = can.Message(
            arbitration_id=Q2Charger.recv_id,
            is_extended_id=True,
            data=[v_msb, v_lsb, c_msb, c_lsb, 0, 0, 0, 0],
            )
        return msg