#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# https://testdriven.io/blog/developing-a-single-page-app-with-fastapi-and-vuejs/
# https://vue-chartjs.org/guide/#custom-new-charts
# https://dev.to/siumhossain/basic-fastapi-websocket-and-vue-3-composition-api-1dhb
# https://tutorials-raspberrypi.com/control-all-gpios-with-the-raspberry-pi-rest-api-via-python/


from typing import Union

import random

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ebc_b20h import EBC_B20H
from q2_charger import Q2Charger


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Initializing battery test devices

try:
    charger = Q2Charger()
    discharger = EBC_B20H()
except:
    print("Couldn't find devices")



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
    return templates.TemplateResponse("index.html", {"request": request, "id": 42})


@app.get("/get_datapoints.json")
def get_datapoints(xstart: int, ystart: int, length: int):
    query_params = {"xstart" : xstart, "ystart": ystart, "length": length}
    y = query_params["ystart"]
    datapoints = []
    for i in range(query_params["length"]):
        y += round(5 + random.random() * (-5-5))
        datapoints.append({ "x": (int(query_params["xstart"]) + i), "y": y})

    return datapoints


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
