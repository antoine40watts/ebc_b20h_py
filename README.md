# Banc de test pour batteries

## Installation

    pip install -r requirements.txt

## Matériel

* Raspberry Pi 3B+
* Testeur de batteries (décharge) ZKTECH EBC-B20H

## Installation du Raspberry Pi

Flashage du système d'exploitation `Raspberry Pi OS` depuis l'image suivante :
https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf.img.xz

Activer SSH sur le raspberry.

Connexion via SSH :

    ssh pi@raspberrypi.local

### Modification du module CAN MCP2515

![MCP2515](https://github.com/antoine40watts/ebc_b20h_py/blob/main/doc/MCP2515%20MODULE.jpg)

Voir https://github.com/tolgakarakurt/CANBus-MCP2515-Raspi

### Installation du logiciel

    git clone https://github.com/antoine40watts/ebc_b20h_py.git
