#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


# from typing import Union
# from enum import Enum
from contextlib import asynccontextmanager
# import asyncio
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

from device import DeviceController


# HOSTNAME = "battest.local"
# HOSTNAME = "127.0.0.1"

logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


class CDRequest(BaseModel):
    cv: float
    cc: float
    dv: float
    dc: float
    nc: int = 1


def new_chart_id():
    global chart_id
    chart_id = str(uuid.uuid1()).split('-')[0]


@asynccontextmanager
async def lifespan(app: FastAPI):
    new_chart_id()
    logging.info("Starting device...")
    device.start()
    logging.info("Device started")
    yield

    await device.stop()    
    print("Bye !")


device = DeviceController()

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

# templates = Jinja2Templates(directory="templates")



# @app.get("/")
# async def read_root():
    # return RedirectResponse("http://"+HOSTNAME+":8000/index")
    # return RedirectResponse(url='index')


# @app.get("/index", response_class=HTMLResponse)
# async def welcome(request: Request):
#     if not discharger.is_monitoring:
#         discharger.start_monitoring()
    
#     return templates.TemplateResponse("index.html", {"request": request, "hostname": HOSTNAME})


class OpRequest(BaseModel):
    operation: str
    params: dict


@app.post("/add-op")
async def add_op(request: OpRequest):
    logging.info("POST request recieved : add operation")
    print(request)
    device.add_operation(request.operation, request.params)
    return {"message": "oh yeah post"}


@app.post("/start-op")
async def start_op():
    logging.info("POST request recieved : start all operations")
    device.start_operations()
    return


@app.post("/stop-op")
async def stop_op():
    logging.info("POST request recieved : stop all operations")
    device.stop_operations()
    return


@app.post("/clear-op")
async def clear_op():
    logging.info("POST request recieved : clear all operations")
    device.clear_operations()
    return {"message": "oh yeah post"}


@app.post("/measure")
async def measure_capacity(request: CDRequest):
    new_chart_id()
    device.measure_capacity(request)
    logging.info("Measure battery capacity request")

    return {"message": "measuring capacity"}


@app.post("/charge")
async def charge_battery(charge_request: CDRequest):
    current = charge_request.cc
    max_voltage = charge_request.cv
    device.charge(current, max_voltage)
    logging.info("Charge battery request")
    return {"message": "Charge request received"}


@app.post("/discharge")
async def discharge_battery(discharge_request: CDRequest):
    current = discharge_request.dc
    min_voltage = discharge_request.dv
    device.discharge(current, min_voltage)
    logging.info("Discharge battery request")
    return {"message": "Discharge request received"}


@app.post("/stop")
async def stop():
    device.stop_all()
    logging.info("Stop all request")
    return {"message": "Stop request received"}


@app.get("/battery-state")
async def get_datapoints(start: int = 0, id: str = ""):
    response = {}

    if chart_id != id:
        start = 0

    if start == 0:
        # First request, will send the current chart id
        response["chart_id"] = chart_id
        print("sending id", chart_id)

    response["battery_state"] = device.batt_state

    if device.batt_capacity > 0:
        response["battery_capacity"] = device.batt_capacity

    datapoints = []
    for datapoint in device.monitoring_data[start:]:
        t, v, c, mah = datapoint
        datapoints.append({"t": round(t, 1), "v": float(v), "c": float(c), "mah": int(mah)})
    response["data"] = datapoints

    response["operations"] = [ {"operation": op, "params": params}
                              for op, params in device.operations ]

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