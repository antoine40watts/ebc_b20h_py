# Banc de test pour batteries

## Matériel

* Raspberry Pi 3B+
* Module CAN MCP2515
* Testeur de batteries (décharge) ZKTECH EBC-B20H
* Chargeur Deligreen Q2-1.5KW

## Installation du Raspberry Pi

Flashage du système d'exploitation `Raspberry Pi OS` (64-bit) avec l'image suivante :
https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-05-03/2023-05-03-raspios-bullseye-arm64-lite.img.xz

Activer SSH sur le raspberry.

Connexion via SSH depuis une machine distante (sous Ubuntu):

    ssh pi@raspberrypi.local

Utiliser l'extension `.local` sous Windows peut nécessiter l'installation du service `Bonjour`.

Mise à jour du système d'exploitation du Raspberry Pi:

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot

### Installation du module CAN MCP2515

![MCP2515](https://github.com/antoine40watts/ebc_b20h_py/blob/main/doc/MCP2515%20MODULE.jpg)

Pour fonctionner avec le niveau de tension des pins GPIO du RasberryPi (3.3V), le module MCP2515 doit être modifié. Il s'agit d'isoler l'alimentation de la puce TJA1050 (transmetteur CAN) pour l'alimenter directement en 5v, alors que le reste du module sera alimenté en 3.3V.

Voir https://github.com/tolgakarakurt/CANBus-MCP2515-Raspi

On peut aussi (et avantageusement) utiliser le module RS485 CAN hat : https://www.waveshare.com/rs485-can-hat.htm

Voir le wiki:
https://www.waveshare.com/wiki/RS485_CAN_HAT

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

Voir https://python-can.readthedocs.io/en/stable/

Pour activer l'interface CAN manuellement :

    sudo /sbin/ip link set can0 up type can bitrate 250000

Pour activer l'interface CAN automatiquement à chaque démarrage du Raspberry Pi, éditer le fichier `/etc/network/interfaces` pour ajouter les lignes :

    auto can0
    iface can0 can static
        bitrate 250000

### Ajouter les droits d'accès au périphérique USB

Créer un fichier `50-ebc_b20h.rules` dans le dossier `/lib/udev/rules.d` et y inscrire la ligne suivante :

    ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="660", GROUP="plugdev"

### Installation du logiciel

    git clone https://github.com/antoine40watts/ebc_b20h_py.git
    pip install -r requirements.txt

### Démarrage du serveur Web (back-end)

    uvicorn main:app --reload --host 0.0.0.0

Ouvrir un navigateur à l'adresse http://localhost:8000

### Démarrage de l'interface Web (front-end)

Depuis le dossier `front`

    npm run dev

Appuyer sur la touche 'o' pour ouvrir le naviguateur sur la page de l'interface.

## Test unitaires

La batterie des tests s'exécute avec la commande suivante (nécessites l'installation de la librairie PIP `pytest`) :

    pytest

## Problèmes

Aucune commande par USB pour activer le mode **CHG** (charge) du EBC-B20H depuis le logiciel officiel, à priori.
J'ai testé quelques commandes différentes, au hasard, mais pas de réaction de l'appareil.

Testé :

    0xFA, 0x03, 0, 0, 0, 0, 0, 0, 0x03, 0xF8  # Aucune réaction
    0xFA, 0x04, 0, 0, 0, 0, 0, 0, 0x04, 0xF8  # Fait planter l'appareil
    0xFA, 0x08, 0, 0, 0, 0, 0, 0, 0x08, 0xF8  # Aucune réaction
    0xFA, 0x09, 0, 0, 0, 0, 0, 0, 0x09, 0xF8  # Aucune réaction
    0xFA, 0x0a, 0, 0, 0, 0, 0, 0, 0x0a, 0xF8  # Aucune réaction

## TODO

* Tests unitaire pour la librairie `q2_charger.py`

## Ressources

Protocole CAN sur Raspberry

* https://www.pragmaticlinux.com/2021/10/can-communication-on-the-raspberry-pi-with-socketcan/
* https://www.beyondlogic.org/adding-can-controller-area-network-to-the-raspberry-pi/
* https://forums.raspberrypi.com/viewtopic.php?t=141052

Interface WEB

* https://fastapi.tiangolo.com
* https://jinja.palletsprojects.com/en/2.10.x/
* https://canvasjs.com

Divers

* https://github.com/JOGAsoft/EBC-controller