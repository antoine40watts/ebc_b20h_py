#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List
import time
import threading
import asyncio
import sys
import logging

import usb.core
import usb.util



class EBC_B20H():
    """
        Serial Commands:
            0x01    Discharge
            0x02    Stop
            0x03    ?
            0x04    Voltage calibration
            0x05    Connect
            0x06    Disconnect
            0x07    Adjust
            0x11    Charge
            0x18    Charge (continue)
    """

    def __init__(self):
        self.buffer = []
        self.debug = False
        self.logfile = "log_ebc-b20.txt"

        self.is_monitoring = False
        self.is_charging = False
        self.is_discharging = False
        self.monitoring_data = []
        self.voltage = 0.0
        self.current = 0.0
        self.mah = 0.0
        
        self.find_device()


    def find_device(self):
        # Vendor ID : QinHeng Electronics
        # Product ID : HL-340 USB-Serial adapter
        dev = usb.core.find(idVendor=0x1a86, idProduct=0x7523)

        if dev is None:
            logging.error("EBC-B20H Discharger not found")
            raise ValueError("EBC-B20H Discharger not found")
        
        self.reattach = False
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
            self.reattach = True
        
        self.dev = dev
        logging.info("EBC-B20H Discharger found")
    

    def destroy(self):
        # This is needed to release interface, otherwise attach_kernel_driver fails
        # due to "Resource busy"
        usb.util.dispose_resources(self.dev)

        # It may raise USBError if there's e.g. no kernel driver loaded at all
        if self.reattach:
            self.dev.attach_kernel_driver(0)
        if self.debug:
            logging.info("Destroying")


    def send(self, message: bytes):
        START_OF_MESSAGE = 0xFA
        END_OF_MESSAGE = 0xF8

        data = [START_OF_MESSAGE]
        data.extend(message)
        data.append(self.checksum(message))
        data.append(END_OF_MESSAGE)

        logging.debug('>>> ' + ' '.join( [f"{str(val):>3}" for val in data] ))

        if self.debug:
            if self.logfile:
                fout = open(self.logfile, 'a')
            else:
                fout = sys.stdout
            print('>>> ' + ' '.join( [f"{str(val):>3}" for val in data] ), file=fout)
            if self.logfile:
                fout.close()

        self.dev.write(0x2, data, 100)


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

        for l in lines:
            logging.debug('<<< ' + ' '.join( [f"{str(val):>3}" for val in l] ))

        if self.debug:
            if self.logfile:
                fout = open(self.logfile, 'a')
            else:
                fout = sys.stdout
            for l in lines:
                print('<<< ' + ' '.join( [f"{str(val):>3}" for val in l] ), file=fout)
            if self.logfile:
                fout.close()
        
        return lines


    def connect(self):
        """
            ZKTECH EBC-B20H handshake between official software and device,
            as seen with a USB Analyzer

            The device won't communicate without connecting first
        """
        
        logging.info("Trying to connect to EBC-B20H")
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
        self.send(bytes([0x05, 0, 0, 0, 0, 0, 0]))


    def disconnect(self):
        self.send(bytes([0x06, 0, 0, 0, 0, 0, 0]))
        if self.is_monitoring:
            self.stop_monitoring()
        if self.debug:
            logging.info("Disconnect command sent")
    

    def stop(self):
        self.send(bytes([0x02, 0, 0, 0, 0, 0, 0]))
        self.is_discharging = False
        if self.debug:
            logging.info("Stop command sent")


    def discharge(self, current=1.0, cutoff_v=2.0):
        """
            Anatomy of a discharge message:
                250   1   4  40   0 200   0   0 229 248
                som dis  c1  c2  v1  v2   ?   ? crc eom
        """
        current = min(max(current, 0.1), 20.0)  # The EBC-B20H is limited to 20Amps discharge current
        cutoff_v = min(max(cutoff_v, 2.0), 72.0)
        c_msb, c_lsb = EBC_B20H.encode_current(current)
        v_msb, v_lsb = EBC_B20H.encode_voltage(cutoff_v)
        
        data = [0x01, c_msb, c_lsb, v_msb, v_lsb, 0, 0]
        
        self.send(bytes(data))
        self.is_discharging = True
        if self.debug:
            logging.info(f"Discharging to {cutoff_v}V @ {current}Amps")


    def adjust(self, current, cutoff_v):
        current = min(max(current, 0.1), 20.0)  # The EBC-B20H is limited to 20Amps discharge current
        cutoff_v = min(max(cutoff_v, 2.0), 72.0)
        c_msb, c_lsb = EBC_B20H.encode_current(current)
        v_msb, v_lsb = EBC_B20H.encode_voltage(cutoff_v)

        data = [0x07, c_msb, c_lsb, v_msb, v_lsb, 0, 0]
        
        self.send(bytes(data))
        if self.debug:
            logging.info("Adjust command sent")


    def charge(self, cutoff_c):
        """ Allow charge (from an external charger)
            until current falls below cutoff_c

            Anatomy of a charge message:
                250 17   0   0   0 200   0   0 229 248
                som ch   ?   ?   ?   ?  c1  c2 crc eom
        """
        c_msb, c_lsb = EBC_B20H.encode_current(cutoff_c)
        data = [0x11, 0, 0, 0, 0xC8, c_msb, c_lsb]
        self.send(bytes(data))
        self.is_charging = True
        if self.debug:
            logging.info("Charge command sent")


    def calibrate(self):
        """ Voltage calibration
            
            Anatomy of a low calibration message:
                250   4   0   4  40   0   0   0  40 248
                som cal  lo  v1  v2             crc eom
            
            Anatomy of a high calibration message:
                250   4   1   4  40   0   0   0  40 248
                som cal  hi   ?   ?             crc eom
            
                !!! voltage encoding is weird here
            
            Anatomy of a calibration validation message:
                250   4   4   0   0   0   0   0   0 248
                som cal val                     crc eom
        """

        raise NotImplementedError
        data = [0x04, 0, 0, 0, 0, 0, 0]
        self.send(bytes(data))


    async def new_monitor(self, callback=None):
        """Send datapoints to logger via a callback function"""
        if self.is_monitoring:
            self.stop_monitoring()
            await self.monitoring_task
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._new_monitor(callback))
    
    async def _new_monitor(self, callback):
        cycle = 2
        while self.is_monitoring:
            data = self.recieve()
            for line in data:
                if not self.is_frame_valid(line):
                    continue
                frame_data = self.decode_frame(line)
                
                status = frame_data['status']
                if status == 0x00 or status == 0x01:
                    self.is_discharging = False
                    self.is_charging = False
                if status == 0x0A:   # Discharging
                    self.is_discharging = True
                    self.is_charging = False
                elif status == 0x0B: # Charging
                    self.is_discharging = False
                    self.is_charging = True
                elif status == 0x14:
                    # end of discharge
                    self.is_discharging = False
                    logging.info("End of discharge")
                elif status == 0x15:
                    # end of charge
                    self.is_charging = False
                    logging.info("End of charge")

                self.voltage = frame_data['voltage']
                self.current = frame_data['current']
                self.mah = frame_data['mah']
                datapoint = [self.voltage, self.current, self.mah]

                # Only record data when device is active
                callback(datapoint)

            await asyncio.sleep(cycle)


    def _monitor(self, filename, raw=False):
        if filename:
            f = open(filename, 'w')
            if not raw:
                f.write("dtime, current, voltage, mah\n")
        
        logging.info("Monitoring thread started")

        while self.is_monitoring:
            data = self.recieve()
            dt = time.time() - self.monitoring_t0
            for line in data:
                if not self.is_frame_valid(line):
                    continue
                frame_data = self.decode_frame(line)

                status = frame_data['status']
                if status == 0x00 or status == 0x01:
                    self.is_discharging = False
                    self.is_charging = False
                if status == 0x0A:   # Discharging
                    self.is_discharging = True
                    self.is_charging = False
                elif status == 0x0B: # Charging
                    self.is_discharging = False
                    self.is_charging = True
                elif status == 0x14:
                    # end of discharge
                    self.is_discharging = False
                    logging.info("End of discharge")
                elif status == 0x15:
                    # end of charge
                    self.is_charging = False
                    logging.info("End of charge")

                self.voltage = frame_data['voltage']
                self.current = frame_data['current']
                self.mah = frame_data['mah']
                datapoint = [dt, self.voltage, self.current, self.mah]

                # Only record data when device is active
                if self.is_charging or self.is_discharging:
                    self.monitoring_data.append(datapoint)

                if raw:
                    formatted = ' '.join([f"{str(val):>3}" for val in line])
                else:
                    formatted = ', '.join(map(str, datapoint))
                if filename:
                    f.write(formatted + '\n')
            time.sleep(2)
        
        logging.info("Monitoring thread stopped")
        
        if filename:
            f.close()
            print("Data file saved to", filename)


    # def start_monitoring(self, filename=None, raw=False):
    #     if self.is_monitoring:
    #         self.stop_monitoring()
        
    #     self.clear()
    #     self.monitoring_t0 = time.time()
    #     self.is_monitoring = True
    #     self.t = threading.Thread(target=self._monitor, args=(filename, raw,))
    #     self.t.setDaemon(True)
    #     self.t.start()
    #     if self.debug:
    #         logging.info("EBC-B20H monitoring started")



    def stop_monitoring(self):
        self.is_monitoring = False
        if self.debug:
            logging.info("EBC-B20H monitoring stopped")


    # def clear(self):
    #     self.monitoring_data.clear()
    #     self.monitoring_t0 = time.time()


    @staticmethod
    def decode_frame(data : List[int]) -> dict:
        amp = EBC_B20H.decode_current(data[2], data[3])
        vbatt = EBC_B20H.decode_voltage(data[4], data[5])
        mah = EBC_B20H.decode_mah(data[6], data[7])
        return {'status': data[1], 'current': amp, 'voltage': vbatt, 'mah': mah}


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
        # The linear transformation to apply is different if the voltage is above 30.00V
        # Weird stuff
        if msb < 149:
            return (msb * 240 + lsb) / 1000
        return (2992 + (msb-149) * 240 + lsb) / 100


    @staticmethod
    def encode_current(current: float) -> Tuple[int, int]:
        # Conversion formulas from https://github.com/JOGAsoft/EBC-controller/blob/main/main.pas
        current *= 1000
        c_msb = int(current / 2400)
        c_lsb = int((current - (c_msb * 2400)) / 10)
        return c_msb, c_lsb


    @staticmethod
    def decode_current(msb: int, lsb: int) -> float:
        return (msb * 240 + lsb) / 100


    @staticmethod
    def encode_mah(mah: int) -> Tuple[int, int]:
        if isinstance(mah, float):
            mah = round(mah)
        if mah >= 10000:
            return divmod(32768 + round(mah/10), 240)
        return divmod(mah, 240)


    @staticmethod
    def decode_mah(msb: int, lsb: int) -> int:
        mah = msb * 240 + lsb
        if mah >= 10000:
            # Above the 9999 mAh threshold
            mah -= 32768
            return mah * 10
        return mah


    @staticmethod
    def checksum(data):
        cs = 0
        for b in data:
            cs = cs^b
        return cs