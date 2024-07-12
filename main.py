#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


from typing import Union
# from enum import Enum
from contextlib import asynccontextmanager
import io
import csv
import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from device import DeviceController
from programs import ProgramStore

from db import searchClients, getClient, updateClient, newClient, deleteClient, addRandomClient
import notion


# HOSTNAME = "battest.local"
# HOSTNAME = "127.0.0.1"

logging.basicConfig(filename='server.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')


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
program_store = ProgramStore("programs.json")

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



class RpcRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Union[list, dict]
    id: int


@app.post("/rpc")
async def rpc(request: RpcRequest):
    logging.info("RPC request")
    print(request)

    result = "RPC went well"

    if request.method == "save_program":
        prog_name = request.params["name"]
        operations = [ {"type": op.type, "params": op.params} for op in device.operations ]
        program_store.add(prog_name, operations)
        result = f"Program '{prog_name}' saved"
    elif request.method == "get_program_names":
        result = program_store.get_names()
    elif request.method == "get_program":
        result = program_store.get(request.params["name"])
    elif request.method == "delete_program":
        prog_name = request.params["name"]
        program_store.delete(prog_name)
        result = f"Program '{prog_name}' deleted"
    elif request.method == "add_operation":
        operation = request.params["type"]
        del request.params["type"]
        device.add_operation(operation, request.params)
        result = f"Operation added: {operation}"
    elif request.method == "add_operations":
        print(request)

        for operation in request.params:
            device.add_operation(operation["type"], operation["params"])
        result = f"Operation added: {operation}"
    else:
        # In case of error
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601, # non-existent method
                "message": f"Method {request.method} doesn't exist"
            },
            "id": request.id,
        }

    print(result)
    return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request.id,
        }


@app.post("/start-ops")
async def start_op():
    logging.info("POST request recieved : start all operations")
    new_chart_id()
    # Clear old chart datapoints
    for op in device.operations:
        op.chart = []
    await device.start_next_operations()
    return {"message": "Operations started"}


@app.post("/stop-ops")
async def stop_op():
    logging.info("POST request recieved : stop all operations")
    await device.stop_all()
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


@app.get("/get-log")
async def get_log(filename: str = "server.log"):
    return FileResponse(path="server.log", filename=filename, media_type="text/plain")



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
            client = notion.getClient(request.params["id"])
            print(client)
            # client.label = f"{client.nom} {client.prenom}"
            return client
        else:
            print("missing 'id' param")

    # elif request.action == "add":
    #     # Add a new client
    #     client = newClient(**request.params)
    #     print(client)
    #     return client
    # elif request.action == "update":
    #     if "id" in request.params and request.params["id"] > 0:
    #         client = updateClient(**request.params)
    #         client.label = f"{client.nom} {client.prenom}"
    #         return client
    #     else:
    #         print("missing 'id' param")



@app.get("/get-clients")
async def get_clients(keyword: str = ""):
    print(keyword)
    client_list = notion.searchClients(keyword)
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