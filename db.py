#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List

import sqlite3
from sqlite3 import Error
from sqlalchemy import (
    create_engine, select,
    ForeignKey,
    Integer, Float, String, JSON, DateTime
)
from sqlalchemy.sql import func, or_
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

import random


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection



class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "client"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_creation: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    date_modification: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    nom: Mapped[str] = mapped_column(String(32), nullable=False)
    prenom: Mapped[str] = mapped_column(String(32), nullable=False)
    adresse: Mapped[Optional[str]] = mapped_column(String(32))
    ville: Mapped[Optional[str]] = mapped_column(String(32))
    cp: Mapped[Optional[str]] = mapped_column(String(32))
    email: Mapped[Optional[str]] = mapped_column(String(32))
    telephone: Mapped[Optional[str]] = mapped_column(String(32))
    batteries: Mapped[List["Battery"]] = relationship(back_populates="client")
    
    def __repr__(self) -> str:
        return f"Client(id={self.id!r}, nom={self.nom!r}, prenom={self.prenom!r})"


class Battery(Base):
    __tablename__ = "battery"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id = mapped_column(ForeignKey("client.id"))
    client: Mapped[Client] = relationship(back_populates="batteries") # What's this ?
    date_creation: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    date_modification: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    marque: Mapped[Optional[str]] = mapped_column(String(32))
    ref_constructeur: Mapped[Optional[str]] = mapped_column(String(32))
    voltage: Mapped[Optional[int]] = mapped_column(Float)
    capacite: Mapped[Optional[int]] = mapped_column(Integer)
    capacite_initiale_mah: Mapped[Optional[int]] = mapped_column(Integer)
    configuration_s: Mapped[Optional[int]] = mapped_column(Integer)
    configuration_p: Mapped[Optional[int]] = mapped_column(Integer)
    
    def __repr__(self) -> str:
        return f"Battery(id={self.id!r}, client_id={self.client_id!r}, voltage={self.voltage!r})"


class BatteryTest(Base):
    __tablename__ = "battery_test"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_creation: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    date_modification: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    data: Mapped[Optional[JSON]] = mapped_column(JSON)


def addRandomClient(n=1):
    # Example: Adding a new client to the database
    for _ in range(n):
        client_prenom = random.choice(["Jean", "Michel", "Louise", "Brigitte", "Lena", "Yann", "John", "David", "Marie", "Raymond", "Hervé", "Fañch"])
        client_nom = random.choice(["Madec", "Dupont", "Quere", "Cueff", "Le Fur", "Doe", "Coat", "Lagadec", "McCullough", "MacLeod", "Le Bihan", "Paugam"])
        new_client = Client(nom=client_nom, prenom=client_prenom, email=f"john.doe@example.com")
        session.add(new_client)
    
    session.commit()



def getClient(id: int) -> Client:
    return session.get(Client, id)


def newClient(**kwargs):
    new_client = Client(
        nom=kwargs["nom"].upper(),
        prenom=kwargs.get("prenom", "").title(),
        adresse=kwargs.get("adresse", ""),
        ville=kwargs.get("ville", ""),
        cp=kwargs.get("cp", ""),
        email=kwargs.get("email", ""),
        telephone=kwargs.get("telephone", ""),
    )
    session.add(new_client)
    session.commit()
    return new_client


def updateClient(id: int, **kwargs) -> None:
    client = getClient(id)
    if "nom" in kwargs:
        client.nom = kwargs["nom"].upper()
    if "prenom" in kwargs:
        client.prenom = kwargs["prenom"].title()
    if "adresse" in kwargs:
        client.adresse = kwargs["adresse"]
    if "ville" in kwargs:
        client.ville = kwargs["ville"].title()
    if "cp" in kwargs:
        client.cp = kwargs["cp"]
    if "email" in kwargs:
        client.email = kwargs["email"]
    if "telephone" in kwargs:
        client.telephone = kwargs["telephone"]
    
    session.commit()
    return client


def deleteClient(id: int) -> None:
    client = getClient(id)
    session.delete(client)
    session.commit()


def addBattery(client: Client, battery: Battery) -> None:
    client.batteries.append(battery)
    session.commit()
    


def searchClients(keyword="") -> List:
    if keyword:
        client_list = session.query(Client).filter(or_(Client.nom.contains(keyword), Client.prenom.contains(keyword)))
    else:
        client_list = session.execute(select(Client)).all()
    
    return client_list


database_url = "sqlite+pysqlite:///test.db"

engine = create_engine(database_url, echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()