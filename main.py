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

# from test.test_ebc_b20h import FakeEBC_B20H



@asynccontextmanager
async def lifespan(app: FastAPI):
    global charger
    global discharger

    # Initializing battery test devices
    charger = Q2Charger()
    discharger = EBC_B20H()
    # discharger = FakeEBC_B20H()
    discharger.connect()
    yield

    # Release USB device
    discharger.stop_monitoring()
    discharger.disconnect()
    print("Bye !")


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None
    


@app.get("/")
def read_root():
    #return {"Hello": "World"}
    return "hello world"


@app.get("/index", response_class=HTMLResponse)
def welcome(request: Request):
    if not discharger.monitoring:
        discharger.start_monitoring()
    
    return templates.TemplateResponse("index.html", {"request": request, "id": 42})


@app.get("/get_datapoints.json")
def get_datapoints():
    # query_params = {"xstart" : xstart, "ystart": ystart, "length": length}
    datapoints = []
    for datapoint in discharger.monitoring_data:
        t, v, c, mah = datapoint
        datapoints.append({"t": t, "v": float(v), "c": float(c), "mah": int(mah)})

    return datapoints


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}



@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down...")
    discharger.disconnect()
