# Script Présence

## Objective 
* Detect the presence of mobiles devices by passively listening at Wifi packets and actively pinging Bluetooth addresses
* Three sub processes: listen Wifi packets on eth0 and mon0 (monitor mode) and ping Bluetooth devices

## Prerequesites
* sudo apt-get install tcpdump
* sudo pip3 install scapy
* sudo apt-get install libbluetooth-dev
* sudo apt-get install python-bluez
* sudo pip3 install pybluez 
* Pour écouter sur l'interface mon0 en mode monitor: See https://github.com/seemoo-lab/nexmon

## Installation du script python pour qu’il s’exécute au démarrage du serveur
1. sudo cp ./presence /etc/init.d/
2. sudo chmod 755 /etc/init.d/presence
3. sudo update-rc.d presence defaults
   * sudo update-rc.d presence remove => pour supprimer le démarrage auto du script
   * "sudo service presence start" pour démarrer le service immédiatement
