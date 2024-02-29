from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple
import logging
import asyncio
import time

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger
from test.test_ebc_b20h import LogEBC_B20H, VirtEBC_B20H
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
    chart: List[Tuple] = field(default_factory=list) # List of datapoints
    #chart: List[Tuple] = field(default=[]) # List of datapoints
    t_start: float = 0.0
    t_end: float = 0.0
    show: bool = True



class DeviceController():
    """ External Device logic is here """

    def __init__(self):
        self.mode = DeviceMode.IDLE
        self.batt_state = BatteryState.IDLE
        self.prev_state = self.batt_state
        self.batt_voltage = 0
        self.batt_current = 0
        self.batt_capacity = 0
        self._running = False
        # self._is_monitoring = False

        try:
            self.charger = Q2Charger()
            self.discharger = EBC_B20H()
        except:
            self.charger = FakeQ2Charger()
            self.discharger = VirtEBC_B20H()
            self.device_error = True
        
        self.discharger.connect()
        #self.monitoring_data = self.discharger.monitoring_data

        self.operations = []
        self.operation_idx = -1


    async def _run(self):
        while self._running:
            # Update battery state
            self.batt_voltage = self.discharger.voltage
            self.batt_current = self.discharger.current
            if self.discharger.is_charging:
                self.batt_state = BatteryState.CHARGING
            elif self.discharger.is_discharging:
                self.batt_state = BatteryState.DISCHARGING
            else:
                self.batt_state = BatteryState.IDLE
            
            # if self.mode == DeviceMode.CAPACITY_TEST:
            #     if self.batt_state == BatteryState.IDLE and self.prev_state == BatteryState.CHARGING:
            #         self.discharge(self.params.dc, self.params.dv)
            #     elif self.batt_state == BatteryState.IDLE and self.prev_state == BatteryState.DISCHARGING:
            #         self.batt_capacity = self.discharger.mah
            #         self.mode = DeviceMode.IDLE
            
            if self.mode == DeviceMode.BETWEEN_OPERATIONS:
                if len(self.operations) > self.operation_idx + 1:
                    # Start the next operation
                    self.start_next_operations()
                else:
                    # End of all operations
                    self.mode = DeviceMode.IDLE
                    self.stop_all()
            
            elif self.mode == DeviceMode.IN_OPERATION:
                current_op = self.operations[self.operation_idx]
                # Check if operation is completed
                if current_op.type != "wait" and \
                        self.batt_state == BatteryState.IDLE and \
                        self.batt_state != self.prev_state:
                    current_op.status = OpStatus.FINISHED
                    current_op.result = (0, "completed")
                    current_op.t_end = time.time()
                    self.batt_capacity = self.discharger.mah
                    self.mode = DeviceMode.BETWEEN_OPERATIONS
                
                if "duration" in current_op.params and current_op.params["duration"] > 0:
                    if time.time() - current_op.t_start >= current_op.params["duration"]:
                        # End of timed operation
                        current_op.status = OpStatus.FINISHED
                        current_op.result = (0, "timeout")
                        current_op.t_end = time.time()
                        self.mode = DeviceMode.BETWEEN_OPERATIONS

            self.prev_state = self.batt_state
            await asyncio.sleep(0.3)
    

    def add_datapoint(self, datapoint):
        """ Add a datapoint to current running operation
            This function should be passed to the monitoring device as a callback
        """
        if not self._running or self.mode != DeviceMode.IN_OPERATION:
            return
        current_op = self.operations[self.operation_idx]
        dt = time.time() - self.monitoring_t0
        datapoint = [dt] + datapoint
        logging.debug(f"Datapoin: {datapoint}")
        if len(current_op.chart) > 0:
            last_datapoint = current_op.chart[-1]
            # Add new datapoint only if values are different from last datapoint
            if datapoint[1:] != last_datapoint[1:]:
                current_op.chart.append(datapoint)
        else:
            current_op.chart.append(datapoint)


    def start(self):
        # Start the device
        self.discharger.new_monitor(self.add_datapoint)
        if not self._running:
            self._running = True
            self.task = asyncio.create_task(self._run())
        logging.info("Device started")
    

    async def stop(self):
        self._running = False
        # self._is_monitoring = False
        await self.discharger.disconnect()

        # Release USB device
        self.discharger.destroy()
        await self.task
        logging.info("Device stopped")
    

    def charge(self, current, max_voltage, adjust=False):
        cutoff_current = 0.5

        if self.discharger.is_discharging:
            self.discharger.stop()
            self.discharger.charge(cutoff_current)
        else:
            self.discharger.charge(cutoff_current)
        
        self.charger.charge(current, max_voltage)

        self.batt_state = BatteryState.CHARGING
        logging.info(f"Charging at {current}Amps and {max_voltage}V max voltage")


    def discharge(self, current, min_voltage, adjust=False):
        if self.charger.is_charging:
            self.charger.stop()
            self.discharger.discharge(current, min_voltage)
        elif adjust:
            self.discharger.adjust(current, min_voltage)
        else:
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
        # self._is_monitoring = False
        if self.charger.is_charging:
            self.charger.stop()
        if self.discharger.is_charging or self.discharger.is_discharging:
            self.discharger.stop()
        self.batt_state = BatteryState.IDLE
        self.mode = DeviceMode.IDLE
        for op in self.operations:
            op.status = OpStatus.PENDING
        self.operation_idx = -1
        logging.info(f"Stop all !")


    def start_next_operations(self):
        # if not self._is_monitoring:
        #     self._is_monitoring = True
        #     self.monitoring_t0 = time.time()
        #     #self.monitoring_task = asyncio.create_task(self._monitor())
        #     self.discharger.new_monitor(self.add_datapoint)
        if self.operation_idx == -1:
            self.monitoring_t0 = time.time()

        self.operation_idx += 1
        if self.operation_idx < len(self.operations):
            current_op = self.operations[self.operation_idx]
            logging.info(f"Starting operation {self.operation_idx}: {current_op.type}")
            print("Start op: " + current_op.type)
            print(current_op.params)
            if current_op.type == "charge":
                current = current_op.params["current"]
                v_max = current_op.params["vlim"]
                self.charge(current, v_max)
            elif current_op.type.startswith("discharge"):
                adjust = "_cont" in current_op.type
                current = current_op.params["current"]
                v_min = current_op.params["vlim"]
                self.discharge(current, v_min, adjust)
            elif current_op.type == "wait":
                self.charger.stop()
                self.discharger.stop()
            current_op.t_start = time.time()
            current_op.status = OpStatus.ONGOING
            self.mode = DeviceMode.IN_OPERATION
    

    def add_operation(self, type: str, params: dict):
        if len(self.operations) > 0:
            if type == "charge" and self.operations[-1].type.startswith("charge"):
                type = "charge_cont"
            elif type == "discharge" and self.operations[-1].type.startswith("discharge"):
                type = "discharge_cont"
        self.operations.append( Operation(type, params) )
        print("op added", type, params)


    def clear_operations(self):
        self.operations.clear()
        self.operation_idx = -1