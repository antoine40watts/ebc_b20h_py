from enum import Enum
import logging
import asyncio

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger
from test.test_ebc_b20h import LogEBC_B20H, VirtEBC_B20H
from test.test_q2_charger import FakeQ2Charger



class DeviceController():
    """ External Device logic is here """

    class BatteryState(Enum):
        IDLE = 0
        CHARGING = 1
        DISCHARGING = 2
    
    class DeviceMode(Enum):
        IDLE = 0
        CAPACITY_TEST = 1


    def __init__(self):
        self.batt_state = self.BatteryState.IDLE
        self.prev_state = self.batt_state
        self.batt_capacity = 0
        self.mode = self.DeviceMode.IDLE
        self._running = False

        try:
            self.charger = Q2Charger()
            self.discharger = EBC_B20H()
        except:
            self.charger = FakeQ2Charger()
            self.discharger = VirtEBC_B20H()
            self.device_error = True
        
        self.discharger.connect()
        self.discharger.start_monitoring()
        self.monitoring_data = self.discharger.monitoring_data

        self.operations = []
        self.current_operation = 0


    async def _run(self):
        while self._running:
            # Update battery state
            if self.discharger.is_charging:
                self.batt_state = self.BatteryState.CHARGING
            elif self.discharger.is_discharging:
                self.batt_state = self.BatteryState.DISCHARGING
            else:
                self.batt_state = self.BatteryState.IDLE
            
            if self.mode == self.DeviceMode.CAPACITY_TEST:
                if self.batt_state == self.BatteryState.IDLE and self.prev_state == self.BatteryState.CHARGING:
                    self.discharge(self.params.dc, self.params.dv)
                elif self.batt_state == self.BatteryState.IDLE and self.prev_state == self.BatteryState.DISCHARGING:
                    self.batt_capacity = self.discharger.mah
                    self.mode = self.DeviceMode.IDLE

            self.prev_state = self.batt_state
            await asyncio.sleep(0.3)
    

    def start(self):
        if not self._running:
            self._running = True
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
        self.batt_state = self.BatteryState.CHARGING
        logging.info(f"Charging at {current}Amps and {max_voltage}V max voltage")


    def discharge(self, current, min_voltage):
        if self.charger.is_charging:
            self.charger.stop()
        self.discharger.discharge(current, min_voltage)
        self.batt_state = self.BatteryState.DISCHARGING
        logging.info(f"Discharging at {current}Amps down to {min_voltage}V")
    

    def measure_capacity(self, request):
        self.mode = self.DeviceMode.CAPACITY_TEST
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
        self.batt_state = self.BatteryState.IDLE
        self.mode = self.DeviceMode.IDLE
        logging.info(f"Stop all !")
    

    def add_operation(self, operation: str, params: dict):
        self.operations.append( (operation, params) )
    

    def clear_operations(self):
        self.operations.clear()
        self.current_operation = 0