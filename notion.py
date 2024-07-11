#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from notion_client import Client
from pprint import pprint


load_dotenv()
    
notion = Client(auth=os.getenv("NOTION_TOKEN"))

database_id = "172db686a4d6479786a1aa44fcba9611"



def get_client_name(client) -> str:
    return client["properties"]["Nom"]["title"][0]["plain_text"]

def get_client_id(client) -> int:
    return client["properties"]["N°client"]["unique_id"]["number"]

def get_client_address(client) -> str:
    address = client["properties"]["Adresse de facturation"]["rich_text"]
    if not address:
        return ""
    
    return address[0]["plain_text"]

def get_client_phone(client) -> str:
    return client["properties"]["Téléphone"]["phone_number"]

def get_client_email(client) -> str:
    return client["properties"]["E-mail"]["email"]


def searchClients(keyword="") -> list:
    if not keyword:
        return []
    
    query_filter = {
        "property": "Nom",
        "title": {"contains": keyword}
    }

    clients = notion.databases.query(database_id, filter=query_filter)
    return [ {"id": get_client_id(client), "label": get_client_name(client)}
            for client in clients["results"] ]


def getClient(id: int) -> dict:
    query_filter = {
        "property": "N°client",
        "unique_id": {"equals": id}
    }

    clients = notion.databases.query(database_id, filter=query_filter)["results"]
    if not clients:
        return
    
    return {
        "id": id,
        "nom": get_client_name(clients[0]),
        "adresse": get_client_address(clients[0]),
        "telephone": get_client_phone(clients[0]),
        "email": get_client_email(clients[0]),
        }


def print_client(query_result):
    def format_client_id(client_id):
        return client_id["prefix"] + str(client_id["number"])

    props = query_result["properties"]
    title = props["Nom"]["title"][0]["plain_text"]
    tel = props["Téléphone"]["phone_number"]
    email = props["E-mail"]["email"]
    client_id = format_client_id(props["N°client"]["unique_id"])
    #print(title, tel, email, client_id)
    print(f"{client_id}\t{title}\t{tel}\t{email}")


if __name__ == "__main__":
    # list_users_response = notion.users.list()
    # pprint(list_users_response)

    #list_databases = notion.databases.retrieve(database_id)
    #pprint(list_databases)

    query_filter = {
            "property": "Nom",
            "title": {"contains": "gue"}
        }

    clients = notion.databases.query(database_id, filter=query_filter)

    #pprint(clients)
    pprint(clients["results"][0])

    for client in clients["results"]:
        print_client(client)

