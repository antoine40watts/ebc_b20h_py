#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from typing import Tuple

import usb.core
import usb.util



def find_device():
    # Vendor ID : QinHeng Electronics
    # Product ID : HL-340 USB-Serial adapter
    dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)

    if dev is None:
        raise ValueError("EBC-B20H Discharger not found")
    
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    
    return dev



def send(dev, data: bytes):
    dev.write(0x2, data, 100)



buffer = []

def recieve(dev):
    global buffer
    
    lines = []
    line = buffer
    
    try:
        data = dev.read(0x82, 128, 200).tolist()
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
    
    buffer = line
    
    return lines



def connect(dev):
    # ZKTECH EBC-B20H handshake between official software and device,
    # as seen with a USB Analyzer
    
    # Control Transfer args :
    # Request type, Request, Value, Index, Data or Size
    dev.ctrl_transfer(0x40, 0xa1, 0xc39c, 0xd98a, None)
    ret = dev.ctrl_transfer(0xc0, 0x95, 0x2c2c, 0x0, 0x2)
    #print(ret)
    dev.ctrl_transfer(0x40, 0x9a, 0xf2c, 0x7, None)
    dev.ctrl_transfer(0x40, 0xa4, 0xdf, 0x0, None)
    dev.ctrl_transfer(0x40, 0xa4, 0x9f, 0x0, None)
    ret = dev.ctrl_transfer(0xc0, 0x95, 0x706, 0x0, 0x2)
    #print(ret)
    dev.ctrl_transfer(0x40, 0x9a, 0x2727, 0x0, None)
    dev.ctrl_transfer(0x40, 0x9a, 0x1312, 0xb282, None)
    ret = dev.ctrl_transfer(0xc0, 0x95, 0x2c2c, 0x0, 0x2)
    #print(ret)
    dev.ctrl_transfer(0x40, 0x9a, 0xf2c, 0x8, None)
    dev.ctrl_transfer(0x40, 0x9a, 0x2518, 0xdb, None)
    ret = dev.ctrl_transfer(0xc0, 0x95, 0x706, 0x0, 0x2)
    #print(ret)
    dev.ctrl_transfer(0x40, 0x9a, 0x2727, 0x0, None)
    
    # "Connect" serial message
    send(dev, bytes([0xFA, 0x05, 0, 0, 0, 0, 0, 0, 0x05, 0xF8]))



def disconnect(dev):
    send(dev, bytes([0xFA, 0x06, 0, 0, 0, 0, 0, 0, 0x06, 0xF8]))



def discharge(dev, current=1.0, vcutoff=2.0):
   
    
    current = min(max(current, 0.1), 20.0)  # The EBC-B20H is limited to 20Amps discharge current
    current *= 1000     # Convert to mA
    c_msb = int(current / 2400)
    c_lsb = int((current - (c_msb * 2400)) / 10)
    
    vcutoff = min(max(vcutoff, 2.0), 72.0)
    vcutoff *= 1000
    v_msb = int(vcutoff / 2400)
    v_lsb = int((vcutoff - (v_msb * 2400)) / 10)
    
    data = [0x01, c_msb, c_lsb, v_msb, v_lsb, 0, 0]
    data = [0xFA] + data + [checksum(data)] + [0xF8]
    
    send(dev, bytes(data))


def encode_voltage(voltage: float) -> Tuple[int, int]:
    # Conversion formulas from https://github.com/JOGAsoft/EBC-controller/blob/main/main.pas
    voltage *= 1000
    v_msb = int(voltage / 2400)
    v_lsb = int((voltage - (v_msb * 2400)) / 10)
    return v_msb, v_lsb


def encode_current(current: float) -> Tuple[int, int]:
    # Conversion formulas from https://github.com/JOGAsoft/EBC-controller/blob/main/main.pas
    current *= 1000
    c_msb = int(current / 2400)
    c_lsb = int((current - (c_msb * 2400)) / 10)
    return c_msb, c_lsb



def stop(dev):
    send(dev, bytes([0xFA, 0x02, 0, 0, 0, 0, 0, 0, 0x02, 0xF8]))



def checksum(data):
    cs = 0
    for b in data:
        cs = cs^b
    return cs



def _monitor(dev, filename):
    global monitoring
    
    f = open(filename, 'w')
    
    while monitoring:
        data = recieve(dev)
        for line in data:
            formated = ' '.join([f'{b:3}' for b in line])
            print(formated)
            f.write(formated + '\n')
        time.sleep(2)
    
    print("Monitoring stopped")
    
    f.close()


def start_monitoring(dev, filename):
    global monitoring
    
    t = threading.Thread(target=_monitor, args=(dev, filename))
    monitoring = True
    t.start()


def stop_monitoring():
    global monitoring
    monitoring = False
    



if __name__ == "__main__":
    

    dev = find_device()
    # print(dev)
    connect(dev)
    
    
    for _ in range(256):
        data = recieve(dev)
        for line in data:
            print(' '.join([f'{b:3}' for b in line]))
        time.sleep(2)
    
    stop(dev)
    
    #time.sleep(3)
    disconnect(dev)

    
    
    
