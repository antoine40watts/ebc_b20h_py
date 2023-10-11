#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


from typing import Union
from enum import Enum
from contextlib import asynccontextmanager
import random
import io
import csv
import uuid

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


# HOSTNAME = "raspberrypi.local"
HOSTNAME = "127.0.0.1"


class BatteryState(Enum):
    IDLE = 0
    CHARGING = 1
    DISCHARGING = 2

battery_state = BatteryState.IDLE

def new_chart_id():
    global chart_id
    chart_id = str(uuid.uuid1()).split('-')[0]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global charger
    global discharger
    global device_error

    # Initializing battery test devices
    try:
        charger = Q2Charger()
        discharger = EBC_B20H()
    except:
        device_error = True
        charger = FakeQ2Charger()
        discharger = FakeEBC_B20H()
        # discharger.discharge

    new_chart_id()
    discharger.connect()
    discharger.start_monitoring()
    yield

    # Release USB device
    discharger.stop_monitoring()
    discharger.disconnect()
    print("Bye !")


app = FastAPI(lifespan=lifespan)

# Allow request from svelte frontend
origins = [
    "http://localhost:5173",
    "http://battest.local:5173"
]

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



class ChargeRequest(BaseModel):
    current: float
    maxVoltage: float

class MeasureRequest(BaseModel):
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
async def measure_capacity(request: MeasureRequest):
    global battery_state

    charge_v = request.cv
    charge_c = request.cc
    discharge_v = request.dv
    discharge_c = request.dc
    num_cycles = request.nc

    discharger.clear()
    new_chart_id()
    charger.charge(charge_c, charge_v)
    battery_state = BatteryState.CHARGING

    return {"message": "measuring capacity"}


# @app.post("/charge")
# async def charge_battery(charge_request: ChargeRequest):
#     global battery_state

#     current = charge_request.current
#     max_voltage = charge_request.maxVoltage

#     charger.charge(current, max_voltage)
#     battery_state = BatteryState.CHARGING
    
#     print(f"Charging at {current}Amps and {max_voltage}V max voltage")

#     return {"message": "Charge request received"}


# @app.post("/discharge")
# async def discharge_battery(charge_request: ChargeRequest):
#     global battery_state
    
#     if charger.is_charging:
#         charger.stop()

#     current = charge_request.current
#     max_voltage = charge_request.maxVoltage

#     discharger.discharge(current, max_voltage)
#     battery_state = BatteryState.DISCHARGING
    
#     print(f"Discharging at {current}Amps and {max_voltage}V max voltage")

#     return {"message": "Discharge request received"}


@app.post("/stop")
async def stop():
    discharger.stop()

    return {"message": "Charge request received"}


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

    response["battery_state"] = battery_state

    datapoints = []
    for datapoint in discharger.monitoring_data[start:]:
        t, v, c, mah = datapoint
        datapoints.append({"t": round(t, 1), "v": float(v), "c": float(c), "mah": int(mah)})
    response["data"] = datapoints

    return response


@app.get("/get-csv")
async def get_datapoints_csv(filename: str = "data.csv"):
    datapoints = [["time (s)", "voltage", "current", "mAh"]]
    for datapoint in discharger.monitoring_data:
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