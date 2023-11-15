from enum import Enum
from dataclasses import dataclass, field
from typing import List
import logging
import asyncio
import time

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger
from test.test_ebc_b20h import FakeEBC_B20H
from test.test_q2_charger import FakeQ2Charger



class BatteryState(Enum):
    IDLE = 0
    CHARGING = 1
    DISCHARGING = 2

class DeviceMode(Enum):
    IDLE = 0
    CAPACITY_TEST = 1
    IN_OPERATION = 2
    BETWEEN_OPERATIONS = 3

class OpStatus(Enum):
    PENDING = 0
    ONGOING = 1
    FINISHED = 2


@dataclass
class Operation():
    type: str
    params: dict
    status: int = OpStatus.PENDING
    result: tuple = (0, "pending")
    #chart: List = field(default=[])
    t_start: float = 0.0
    t_end: float = 0.0
    show: bool = True



class DeviceController():
    """ External Device logic is here """

    def __init__(self):
        self.batt_state = BatteryState.IDLE
        self.prev_state = self.batt_state
        self.batt_capacity = 0
        self.mode = DeviceMode.IDLE
        self._running = False

        try:
            self.charger = Q2Charger()
            self.discharger = EBC_B20H()
        except:
            self.charger = FakeQ2Charger()
            self.discharger = FakeEBC_B20H()
            self.device_error = True
        
        self.discharger.connect()
        self.discharger.start_monitoring()
        self.monitoring_data = self.discharger.monitoring_data

        self.operations = []
        self.operation_idx = 0


    async def _run(self):
        while self._running:
            # Update battery state
            if self.discharger.is_charging:
                self.batt_state = BatteryState.CHARGING
            elif self.discharger.is_discharging:
                self.batt_state = BatteryState.DISCHARGING
            else:
                self.batt_state = BatteryState.IDLE
            
            if self.mode == DeviceMode.CAPACITY_TEST:
                if self.batt_state == BatteryState.IDLE and self.prev_state == BatteryState.CHARGING:
                    self.discharge(self.params.dc, self.params.dv)
                elif self.batt_state == BatteryState.IDLE and self.prev_state == BatteryState.DISCHARGING:
                    self.batt_capacity = self.discharger.mah
                    self.mode = DeviceMode.IDLE
            
            if self.mode == DeviceMode.BETWEEN_OPERATIONS:
                if len(self.operations) > self.operation_idx + 1:
                    # Start the next operation
                    self.operation_idx += 1
                    next_op = self.operations[self.operation_idx]
                    next_op.status = OpStatus.ONGOING
                    next_op.t_start = time.time()
                else:
                    self.mode = DeviceMode.IDLE
            elif self.mode == DeviceMode.IN_OPERATION:
                current_op = self.operations[self.operation_idx]
                if "duration" in current_op.params and current_op.params["duration"] > 0:
                    if time.time() - current_op.t_start >= current_op.params["duration"]:
                        # End of timed operation
                        current_op.status = OpStatus.FINISHED
                        current_op.result = (0, "no comment")
                        current_op.t_end = time.time()
                        self.mode == DeviceMode.BETWEEN_OPERATIONS

            self.prev_state = self.batt_state
            await asyncio.sleep(0.3)
    

    def start(self):
        if not self._running:
            self._running = True
            self.t0 = time.time()
            self.task = asyncio.create_task(self._run())
            # await self.task
    

    async def stop(self):
        self._running = False
        self.discharger.stop_monitoring()
        self.discharger.disconnect()

        # Release USB device
        self.discharger.destroy()
        await self.task
    

    def charge(self, current, max_voltage):
        if self.discharger.is_discharging:
            self.discharger.stop()
        self.charger.charge(current, max_voltage)
        self.discharger.charge(cutoff_c = 0.1)
        self.batt_state = BatteryState.CHARGING
        logging.info(f"Charging at {current}Amps and {max_voltage}V max voltage")


    def discharge(self, current, min_voltage):
        if self.charger.is_charging:
            self.charger.stop()
        self.discharger.discharge(current, min_voltage)
        self.batt_state = BatteryState.DISCHARGING
        logging.info(f"Discharging at {current}Amps down to {min_voltage}V")
    

    def measure_capacity(self, request):
        self.mode = DeviceMode.CAPACITY_TEST
        self.params = request
        self.charger.charge(request.cc, request.cv)
        self.discharger.charge(cutoff_c = 0.1)
        self.discharger.clear()
        self.batt_capacity = 0
        logging.info(f"Measuring capacity")
    

    def stop_all(self):
        if self.charger.is_charging:
            self.charger.stop()
        if self.discharger.is_charging or self.discharger.is_discharging:
            self.discharger.stop()
        self.batt_state = BatteryState.IDLE
        self.mode = DeviceMode.IDLE
        logging.info(f"Stop all !")


    def start_operations(self):
        if self.operations:
            self.mode = DeviceMode.IN_OPERATION
            self.t0 = time.time()
    

    def add_operation(self, type: str, params: dict):
        self.operations.append( Operation(type, params) )
    

    def clear_operations(self):
        self.operations.clear()
        self.operation_idx = 0
    