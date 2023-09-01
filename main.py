#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


from typing import Union
from contextlib import asynccontextmanager

import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger

from test.test_ebc_b20h import FakeEBC_B20H



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
        discharger = FakeEBC_B20H()

    discharger.connect()
    yield

    # Release USB device
    discharger.stop_monitoring()
    discharger.disconnect()
    print("Bye !")


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



class ChargeRequest(BaseModel):
    current: float
    maxVoltage: float
    


@app.get("/")
def read_root():
    #return {"Hello": "World"}
    return "hello world"


@app.get("/index", response_class=HTMLResponse)
def welcome(request: Request):
    if not discharger.monitoring:
        discharger.start_monitoring()
    
    return templates.TemplateResponse("index.html", {"request": request, "id": 42})


@app.post("/charge")
async def charge_battery(charge_request: ChargeRequest):
    current = charge_request.current
    max_voltage = charge_request.maxVoltage

    charger.charge(current, max_voltage)
    print(f"Charging at {current}Amps and {max_voltage}V max voltage")

    return {"message": "Charge request received"}


@app.get("/get_datapoints.json")
def get_datapoints():
    # query_params = {"xstart" : xstart, "ystart": ystart, "length": length}
    datapoints = []
    for datapoint in discharger.monitoring_data:
        t, v, c, mah = datapoint
        datapoints.append({"t": t, "v": float(v), "c": float(c), "mah": int(mah)})

    return datapoints
