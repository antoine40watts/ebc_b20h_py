#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List
import time
import threading

import usb.core
import usb.util



class EBC_B20H():

    def __init__(self):
        self.buffer = []
        self.monitoring = False
        self.monitoring_data = []
        self.find_device()


    def find_device(self):
        # Vendor ID : QinHeng Electronics
        # Product ID : HL-340 USB-Serial adapter
        dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)

        if dev is None:
            raise ValueError("EBC-B20H Discharger not found")
        
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        
        self.dev = dev


    def send(self, data: bytes):
        self.dev.write(0x2, data, 100)


    def recieve(self):        
        lines = []
        line = self.buffer
        
        try:
            data = self.dev.read(0x82, 128, 200).tolist()
        except usb.core.USBTimeoutError:
            return []
            
        for b in data:
            if b == 250:    # Start of new message
                if line:
                    lines.append(line)
                line = [b]
            elif b == 248:  # End of message
                line.append(b)
                lines.append(line)
                line = []
            else:
                line.append(b)
        self.buffer = line
        
        return lines


    def connect(self):
        # ZKTECH EBC-B20H handshake between official software and device,
        # as seen with a USB Analyzer
        
        # Control Transfer args : Request type, Request, Value, Index, Data or Size
        self.dev.ctrl_transfer(0x40, 0xa1, 0xc39c, 0xd98a, None)
        ret = self.dev.ctrl_transfer(0xc0, 0x95, 0x2c2c, 0x0, 0x2)
        #print(ret)
        self.dev.ctrl_transfer(0x40, 0x9a, 0xf2c, 0x7, None)
        self.dev.ctrl_transfer(0x40, 0xa4, 0xdf, 0x0, None)
        self.dev.ctrl_transfer(0x40, 0xa4, 0x9f, 0x0, None)
        ret = self.dev.ctrl_transfer(0xc0, 0x95, 0x706, 0x0, 0x2)
        #print(ret)
        self.dev.ctrl_transfer(0x40, 0x9a, 0x2727, 0x0, None)
        self.dev.ctrl_transfer(0x40, 0x9a, 0x1312, 0xb282, None)
        ret = self.dev.ctrl_transfer(0xc0, 0x95, 0x2c2c, 0x0, 0x2)
        #print(ret)
        self.dev.ctrl_transfer(0x40, 0x9a, 0xf2c, 0x8, None)
        self.dev.ctrl_transfer(0x40, 0x9a, 0x2518, 0xdb, None)
        ret = self.dev.ctrl_transfer(0xc0, 0x95, 0x706, 0x0, 0x2)
        #print(ret)
        self.dev.ctrl_transfer(0x40, 0x9a, 0x2727, 0x0, None)
        
        # "Connect" serial message
        self.send(bytes([0xFA, 0x05, 0, 0, 0, 0, 0, 0, 0x05, 0xF8]))


    def disconnect(self):
        self.send(bytes([0xFA, 0x06, 0, 0, 0, 0, 0, 0, 0x06, 0xF8]))


    def discharge(self, current=1.0, vcutoff=2.0):
        current = min(max(current, 0.1), 20.0)  # The EBC-B20H is limited to 20Amps discharge current
        vcutoff = min(max(vcutoff, 2.0), 72.0)
        c_msb, c_lsb = self.encode_current(current)
        v_msb, v_lsb = self.encode_voltage(vcutoff)
        
        data = [0x01, c_msb, c_lsb, v_msb, v_lsb, 0, 0]
        data = [0xFA] + data + [EBC_B20H.checksum(data)] + [0xF8]
        
        self.send(bytes(data))


    def adjust(self, current, vcutoff):
        current = min(max(current, 0.1), 20.0)  # The EBC-B20H is limited to 20Amps discharge current
        vcutoff = min(max(vcutoff, 2.0), 72.0)
        c_msb, c_lsb = self.encode_current(current)
        v_msb, v_lsb = self.encode_voltage(vcutoff)

        data = [0x07, c_msb, c_lsb, v_msb, v_lsb, 0, 0]
        data = [0xFA] + data + [self.checksum(data)] + [0xF8]
        
        self.send(bytes(data))


    def stop(self):
        self.send(bytes([0xFA, 0x02, 0, 0, 0, 0, 0, 0, 0x02, 0xF8]))


    @staticmethod
    def decode_frame(data : List[int]) -> dict:
        amp = EBC_B20H.decode_current(data[2], data[3])
        vbatt = EBC_B20H.decode_voltage(data[4], data[5])
        mah = EBC_B20H.decode_mah(data[6], data[7])
        return {'current': amp, 'voltage': vbatt, 'mah': mah}


    @staticmethod
    def is_frame_valid(data: List[int]) -> bool:
        if len(data) != 19:
            return False
        return EBC_B20H.checksum(data[1: -2]) == data[-2]


    @staticmethod
    def encode_voltage(voltage: float) -> Tuple[int, int]:
        # Conversion formulas from https://github.com/JOGAsoft/EBC-controller/blob/main/main.pas
        voltage *= 1000
        v_msb = int(voltage / 2400)
        v_lsb = int((voltage - (v_msb * 2400)) / 10)
        return v_msb, v_lsb


    @staticmethod
    def decode_voltage(msb: int, lsb: int) -> float:
        return (msb * 2400 + lsb * 10) / 10000


    @staticmethod
    def encode_current(current: float) -> Tuple[int, int]:
        # Conversion formulas from https://github.com/JOGAsoft/EBC-controller/blob/main/main.pas
        current *= 1000
        c_msb = int(current / 2400)
        c_lsb = int((current - (c_msb * 2400)) / 10)
        return c_msb, c_lsb


    @staticmethod
    def decode_current(msb: int, lsb: int) -> float:
        return (msb * 2400 + lsb * 10) / 1000


    @staticmethod
    def decode_mah(msb: int, lsb: int) -> int:
        return round((msb * 2400 + lsb * 10) / 10)


    @staticmethod
    def checksum(data):
        cs = 0
        for b in data:
            cs = cs^b
        return cs


    def _monitor(self, filename):
        if filename:
            f = open(filename, 'w')
            f.write("dtime, current, voltage, mah\n")
        
        while self.monitoring:
            data = self.recieve()
            dt = time.time() - self.monitoring_t0
            for line in data:
                if not self.is_frame_valid(line):
                    continue
                frame_data = self.decode_frame(line)
                # print(frame_data)
                datapoint = [dt, frame_data['voltage'], frame_data['current'], frame_data['mah']]
                self.monitoring_data.append(datapoint)
                formatted = ', '.join(map(str, datapoint))
                # print(formatted)

                if filename:
                    f.write(formatted + '\n')
            time.sleep(2)
        
        print("Monitoring stopped")
        
        if filename:
            f.close()
            print("Data file saved to", filename)


    def start_monitoring(self, filename=None):        
        self.monitoring = True
        self.monitoring_data.clear()
        self.monitoring_t0 = time.time()
        self.t = threading.Thread(target=self._monitor, args=(filename,))
        self.t.start()


    def stop_monitoring(self):
        self.monitoring = False
        self.t.join()
