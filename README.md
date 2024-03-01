# Banc de test pour batteries

## Matériel

* Raspberry Pi 3B+
* Module CAN MCP2515 ou RS485
* Testeur de batteries (décharge) ZKTECH EBC-B20H
* Chargeur Deligreen Q2-1.5KW

## Installation du Raspberry Pi

Flashage du système d'exploitation `Raspberry Pi OS` (64-bit) avec l'image suivante :
https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-05-03/2023-05-03-raspios-bullseye-arm64-lite.img.xz

### Mise en route du serveur SSH

Activer SSH sur le raspberry :
Créer un fichier nommé `ssh` dans la partition `boot` du système de fichier du raspberry.
Créer un second fichier, nommé `userconf.txt` contenant la ligne `username:password`, ou `password` est à remplacer par le hash généré par la commande `openssl passwd -6` et `username` par le nom d'utilisateur de votre choix.

Connexion via SSH depuis une machine distante (sous Ubuntu):

    ssh username@raspberrypi.local

Utiliser l'extension `.local` sous Windows peut nécessiter l'installation du service `Bonjour`.

### Configuration du WiFi

https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-networking

Lancer l'utilitaire `raspi-config`, dans `Localisation Options`, définir le pays dans le menu `WLAN Country`.

On peut afficher la liste des réseaux Wifi disponibles avec la commande `sudo iwlist wlan0 scan`.

Pour ajouter une connexion Wifi, éditer le fichier `wpa-supplicant` :

    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

Ajouter les lignes :

    network={
        ssid="testing"
        psk="testingPassword"
    }

Exécuter la ligne `wpa_cli -i wlan0 reconfigure` pour mettre à jour la configuration.

### Mise à jour

Mise à jour du système d'exploitation du Raspberry Pi:

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot

### Installation du module CAN

#### Module MCP2515

![MCP2515](https://github.com/antoine40watts/ebc_b20h_py/blob/main/doc/MCP2515%20MODULE.jpg)

Pour fonctionner avec le niveau de tension des pins GPIO du RasberryPi (3.3V), le module MCP2515 doit être modifié. Il s'agit d'isoler l'alimentation de la puce TJA1050 (transmetteur CAN) pour l'alimenter directement en 5v, alors que le reste du module sera alimenté en 3.3V.

Voir https://github.com/tolgakarakurt/CANBus-MCP2515-Raspi

#### Module RS485

Module basé sur le MCP2515, cadencé à 12 MHz et adapté au Raspberry PI.

Boutique : https://www.waveshare.com/rs485-can-hat.htm

Voir le wiki:
https://www.waveshare.com/wiki/RS485_CAN_HAT

Activer l'interface SPI depuis l'outil `raspi-config`.

Éditer le fichier `/boot/config.txt`. Vérifier que la ligne `dtparam=spi=on` est bien présente, et ajouter la ligne :

    dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25,spimaxfrequency=2000000

Si le quartz de votre module MCP2515 est cadencé à 12MHz, remplacer la valeur `8000000` par `12000000`.

La valeur `interrupt` correspond au port GPIO sur lequel est branché le pin `int` du module MCP2515.

Après redémarrage du Raspberry Pi, on peut vérifer la bonne connection du module MCP2515 avec la commande :

    dmesg | grep "spi"

### Module infrarouge MLX90640

Librairie : https://pypi.org/project/seeed-python-mlx90640/

Le module d'alimente en 3V.
Brancher le SDA du module sur le SDA du Raspberry PI (pin 3). Brancher le SCL du module sur le SCL du Raspberry PI (pin 5).

Éditer le fichier `/boot/config.txt` pour ajouter la ligne `dtparam=i2c_arm=on,i2c_arm_baudrate=400000`.

### Installation automatique du logiciel

    sudo apt install git
    git clone https://github.com/antoine40watts/ebc_b20h_py.git
    sudo ./install.sh

### Installation manuelle du logiciel

Les instructions suivantes sont équivalentes à celles exécutées par le script d'installation `install.sh`.

Installation des outils de communication avec l'interface CAN :

    sudo apt install can-utils
    sudo apt install python3-pip
    sudo pip3 install python-can

Voir https://python-can.readthedocs.io/en/stable/

Pour activer l'interface CAN manuellement :

    sudo /sbin/ip link set can0 up type can bitrate 250000

Pour activer l'interface CAN automatiquement à chaque démarrage du Raspberry Pi, éditer le fichier `/etc/network/interfaces` pour ajouter les lignes :

    auto can0
    iface can0 can static
        bitrate 250000

### Ajouter les droits d'accès au périphérique USB

Créer un fichier `99-ebc_b20h.rules` dans le dossier `/lib/udev/rules.d` et y inscrire la ligne suivante :

    ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="660", GROUP="plugdev"

### Démarrage du serveur Web (back-end)

    uvicorn main:app --reload --host 0.0.0.0

Ouvrir un navigateur à l'adresse http://localhost:8000

### Démarrage de l'interface Web (front-end)

Depuis le dossier `front`

    npm run dev

Appuyer sur la touche 'o' pour ouvrir le naviguateur sur la page de l'interface.

## Réglage des problèmes

Pour développer l'application en local, sans avoir besoin du matériel réel, il suffit de définir le paramètre `VITE_PROD` à `false` dans le fichier `.env`.

L'interface web sera alors accessible à l'adresse http://localhost:5173

Une fois connecté en SSH sur le raspberry pi, on peut contrôler l'état du serveur avec

    systemctl status battest

On peut mettre en arrêt le service avec

    systemctl stop battest

Lecture du journal

    journalctl -u battest -r

## Test unitaires

La batterie des tests s'exécute avec la commande suivante (nécessites l'installation de la librairie PIP `pytest`) :

    pytest

## Ressources

Protocole CAN sur Raspberry

* https://www.pragmaticlinux.com/2021/10/can-communication-on-the-raspberry-pi-with-socketcan/
* https://www.beyondlogic.org/adding-can-controller-area-network-to-the-raspberry-pi/
* https://forums.raspberrypi.com/viewtopic.php?t=141052
* https://stackoverflow.com/questions/3738173/why-does-pyusb-libusb-require-root-sudo-permissions-on-linux

Interface WEB

* https://fastapi.tiangolo.com
* https://jinja.palletsprojects.com/en/2.10.x/
* https://canvasjs.com

Divers

* https://github.com/JOGAsoft/EBC-controller
