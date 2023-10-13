#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


from typing import Union
from enum import Enum
from contextlib import asynccontextmanager
import asyncio
import random
import io
import csv
import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger

from test.test_ebc_b20h import FakeEBC_B20H
from test.test_q2_charger import FakeQ2Charger


HOSTNAME = "battest.local"
# HOSTNAME = "127.0.0.1"



class DeviceController():
    """ External Device logic is here """

    class BatteryState(Enum):
        IDLE = 0
        CHARGING = 1
        DISCHARGING = 2
    

    def __init__(self):
        self.battery_state = self.BatteryState.IDLE
        # self.state = 
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

    async def _run(self):
        print("runnnn")
        while self._running:
            if self.discharger.is_charging:
                self.battery_state = self.BatteryState.CHARGING
            elif self.discharger.is_discharging:
                self.battery_state = self.BatteryState.DISCHARGING
            else:
                self.battery_state = self.BatteryState.IDLE
            
            await asyncio.sleep(1)
    
    def start_monitoring(self):
        print("device start monit")
        if not self._running:
            self._running = True
            self.task = asyncio.create_task(self._run())
            # await self.task
    
    def stop_monitoring(self):
        self._running = False
        self.discharger.stop_monitoring()
        self.discharger.disconnect()
        # Release USB device
        self.discharger.destroy()
    
    def charge(self, current, max_voltage):
        self.charger.charge(current, max_voltage)
        self.discharger.charge(cutoff_c = 0.1)
        logging.info(f"Charging at {current}Amps and {max_voltage}V max voltage")

    def discharge(self, current, min_voltage):
        if charger.is_charging:
            self.charger.stop()
        self.discharger.discharge(current, min_voltage)
        logging.info(f"Discharging at {current}Amps down to {max_voltage}V")
    
    def stop_all(self):
        if self.charger.is_charging:
            self.charger.stop()
        if self.discharger.is_charging or discharger.is_discharging:
            self.discharger.stop()

        logging.debug("Server: stop request")




def new_chart_id():
    global chart_id
    chart_id = str(uuid.uuid1()).split('-')[0]


@asynccontextmanager
async def lifespan(app: FastAPI):
    new_chart_id()
    print("starting device")
    device.start_monitoring()
    print("device started")
    yield

    device.stop_monitoring()    
    print("Bye !")



device = DeviceController()

logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

app = FastAPI(lifespan=lifespan)

# Allow request from svelte frontend
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# Svelte mount point
# app.mount("/front", StaticFiles(directory="front/public", html=True), name="front")

templates = Jinja2Templates(directory="templates")


class CDRequest(BaseModel):
    cv: float
    cc: float
    dv: float
    dc: float
    nc: int = 1


@app.get("/")
async def read_root():
    # return RedirectResponse("http://"+HOSTNAME+":8000/index")
    return RedirectResponse(url='index')


# @app.get("/index", response_class=HTMLResponse)
# async def welcome(request: Request):
#     if not discharger.is_monitoring:
#         discharger.start_monitoring()
    
#     return templates.TemplateResponse("index.html", {"request": request, "hostname": HOSTNAME})


@app.post("/measure")
async def measure_capacity(request: CDRequest):
    # global battery_state

    charge_v = request.cv
    charge_c = request.cc
    discharge_v = request.dv
    discharge_c = request.dc
    num_cycles = request.nc

    new_chart_id()
    discharger.clear()
    charger.charge(charge_c, charge_v)
    discharger.charge(cutoff_c = 0.1)

    return {"message": "measuring capacity"}


@app.post("/charge")
async def charge_battery(charge_request: CDRequest):
    current = charge_request.cc
    max_voltage = charge_request.cv
    device.charge(current, max_voltage)
    
    return {"message": "Charge request received"}


@app.post("/discharge")
async def discharge_battery(discharge_request: CDRequest):
    current = discharge_request.dc
    min_voltage = discharge_request.dv
    device.discharge(current, min_voltage)
    
    return {"message": "Discharge request received"}


@app.post("/stop")
async def stop():
    device.stop_all()
    return {"message": "Stop request received"}


@app.get("/battery-state")
async def get_datapoints(start: int = 0, id: str = ""):
    # query_params = {"start" : start}
    print(f"{start=} {id=}")
    response = {}

    if chart_id != id:
        start = 0

    if start == 0:
        # First request, will send the current chart id
        response["chart_id"] = chart_id
        print("sending id", chart_id)

    response["battery_state"] = device.battery_state

    datapoints = []
    for datapoint in device.monitoring_data[start:]:
        t, v, c, mah = datapoint
        datapoints.append({"t": round(t, 1), "v": float(v), "c": float(c), "mah": int(mah)})
    response["data"] = datapoints

    return response


@app.get("/get-csv")
async def get_datapoints_csv(filename: str = "data.csv"):
    datapoints = [["time (s)", "voltage", "current", "mAh"]]
    for datapoint in device.monitoring_data:
        t, v, c, mah = datapoint
        datapoints.append([round(t), round(v, 2), round(c, 2), int(mah)])

    # Create a CSV stream
    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerows(datapoints)

    # Prepare the CSV response
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = 'attachment; filename={}'.format(filename)

    return response