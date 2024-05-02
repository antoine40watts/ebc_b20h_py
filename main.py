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
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from device import DeviceController

from db import searchClients, getClient, updateClient, newClient, deleteClient, addRandomClient


# HOSTNAME = "battest.local"
# HOSTNAME = "127.0.0.1"

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(message)s')


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
    print(searchClients())
    # addRandomClient(8)

    new_chart_id()
    logging.info("Starting device...")
    print("starting device (print)")
    await device.start()
    logging.info("Device started")
    yield

    await device.stop()
    print("Bye !")


device = DeviceController()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allow request from svelte frontend
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
    return {"message": "Operation added: " + str(device.operations[-1])}


@app.post("/start-ops")
async def start_op():
    logging.info("POST request recieved : start all operations")
    new_chart_id()
    # Clear old chart datapoints
    for op in device.operations:
        op.chart = []
    device.start_next_operations()
    return {"message": "Operations started"}


@app.post("/stop-ops")
async def stop_op():
    logging.info("POST request recieved : stop all operations")
    device.stop_all()
    return {"message": "Operations stopped"}


@app.post("/delete-op")
async def delete_op(idx: int = -1):
    logging.info("POST request recieved : delete operation")
    device.delete_operation(idx)

@app.post("/clear-ops")
async def clear_op():
    logging.info("POST request recieved : clear all operations")
    device.clear_operations()
    return {"message": "Operations cleared"}


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

    # Reset chart to t0
    # device.discharger.clear()
    # new_chart_id()

    device.charge(current, max_voltage)
    logging.info("Charge battery request")
    return {"message": "Charge request received"}


@app.post("/discharge")
async def discharge_battery(discharge_request: CDRequest):
    current = discharge_request.dc
    min_voltage = discharge_request.dv

    # Reset chart to t0
    # device.discharger.clear()
    # new_chart_id()

    device.discharge(current, min_voltage)
    logging.info("Discharge battery request")
    return {"message": "Discharge request received"}


@app.post("/stop")
async def stop():
    device.stop_all()
    logging.info("Stop all request")
    return {"message": "Stop request received"}


@app.get("/get-state")
async def get_device_state(start: int = 0, id: str = ""):
    """
        Sent data :
            device_state <DeviceMode>
            battery_state <BatteryState>
            chart_data <list>             (graph points)
            operations <list>       (recorded operations)
            battery_capacity <int>  (displayed mAh)
    """
    response = {}

    # if chart_id != id:
    #     start = 0

    # if start == 0:
    #     # First request, will send the current chart id
    #     response["chart_id"] = chart_id
    #     print("sending id", chart_id)

    response["device_mode"] = device.mode
    response["battery_state"] = device.batt_state
    response["battery_voltage"] = device.batt_voltage
    response["battery_current"] = device.batt_current
    response["battery_mah"] = device.discharger.mah
    response["battery_capacity"] = device.batt_capacity

    response["operations"] = [
                            {"type": op.type,
                                "params": op.params,
                                "status": op.status,
                                "chart": op.chart,
                                }
                            for op in device.operations ]

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




## Database stuff

class DBAction(BaseModel):
    table_name: str
    action: str # Add, Update, Delete
    params: dict


@app.post("/db-action/")
async def db_action(request: DBAction):
    if request.action == "get":
        # Request a client with given 'id' from database
        if "id" in request.params and request.params["id"] > 0:
            client = getClient(request.params["id"])
            client.label = f"{client.nom} {client.prenom}"
            return client
        else:
            print("missing 'id' param")
    elif request.action == "add":
        # Add a new client
        client = newClient(**request.params)
        print(client)
        return client
    elif request.action == "update":
        if "id" in request.params and request.params["id"] > 0:
            client = updateClient(**request.params)
            client.label = f"{client.nom} {client.prenom}"
            return client
        else:
            print("missing 'id' param")



@app.get("/get-clients")
async def get_clients(keyword: str = ""):
    client_list = searchClients(keyword)
    client_list = [
            { "id": c.id, "label": f"{c.nom.upper()} {c.prenom}" }
            for c in client_list ]
    return client_list


class Client(BaseModel):
    id: int
    nom: str
    prenom: str
    adresse: str
    ville: str
    phone: str
    email: str


@app.delete("/delete-client")
async def delete_client(id: int):
    print("deleting", id)
    deleteClient(id)
    # return JSONResponse(status_code=204)



## Battery Item functions

class Battery(BaseModel):
    id: int
    client_id: int