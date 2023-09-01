# Banc de test pour batteries

## Installation

    pip install -r requirements.txt

## Matériel

* Raspberry Pi 3B+
* Module CAN MCP2515
* Testeur de batteries (décharge) ZKTECH EBC-B20H
* Chargeur Deligreen Q2-1.5KW

## Installation du Raspberry Pi

Flashage du système d'exploitation `Raspberry Pi OS` depuis l'image suivante :
https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf.img.xz

Activer SSH sur le raspberry.

Connexion via SSH depuis une machine distante (sous Ubuntu):

    ssh pi@raspberrypi.local

Utiliser l'extension `.local` sous Windows nécessite l'installation de `Bonjour`.

Mise à jour du système d'exploitation du Raspberry Pi:

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot

### Installation du module CAN MCP2515

![MCP2515](https://github.com/antoine40watts/ebc_b20h_py/blob/main/doc/MCP2515%20MODULE.jpg)

Pour fonctionner avec le niveau de tension des pins GPIO du RasberryPi (3.3V), le module MCP2515 doit être modifié. Il s'agit d'isoler l'alimentation de la puce TJA1050 (transmetteur CAN) pour l'alimenter directement en 5v, alors que le reste du module sera alimenté en 3.3V.

Voir https://github.com/tolgakarakurt/CANBus-MCP2515-Raspi

On peut aussi (et avantageusement) utiliser le module RS485 CAN hat : https://www.waveshare.com/rs485-can-hat.htm

Activer l'interface SPI depuis l'outil `raspi-config`.

Éditer le fichier `/boot/config.txt`. Vérifier que la ligne `dtparam=spi=on` est bien présente, et ajouter la ligne :

    dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25

Si le quartz de votre module MCP2515 est cadencé à 12MHz, remplacer la valeur `8000000` par `12000000`.

La valeur `interrupt` correspond au port GPIO sur lequel est branché le pin `int` du module MCP2515.

Après redémarrage du Raspberry Pi, on peut vérifer la bonne connection du module MCP2515 avec la commande :

    dmesg | grep "spi"

Installation des outils de communication avec l'interface CAN :

    sudo apt-get install can-utils
    sudo pip3 install python-can

Pour activer l'interface CAN manuellement :

    sudo /sbin/ip link set can0 up type can bitrate 250000

### Installation du logiciel

    git clone https://github.com/antoine40watts/ebc_b20h_py.git

### Démarrage du serveur Web

    uvicorn main:app --reload

## Ressources

* https://www.pragmaticlinux.com/2021/10/can-communication-on-the-raspberry-pi-with-socketcan/
* https://www.beyondlogic.org/adding-can-controller-area-network-to-the-raspberry-pi/