# Script Présence

## Goal 
* Detect packets from specific MAC addresses (from mobile phone for example) and trigger events
* Two threads : listen on eth0 and on mon0 (monitor mode)

## Pré requis
* sudo apt-get install tcpdump
* pip install --user scapy
* Pour écouter sur l'interface mon0 en mode monitor: See https://github.com/seemoo-lab/nexmon

## Installation du script python pour qu’il s’exécute au démarrage du serveur
1. sudo cp ./presence /etc/init.d/
2. sudo chmod 755 /etc/init.d/presence
3. sudo update-rc.d presence defaults
   * sudo update-rc.d presence remove => pour supprimer le démarrage auto du script
   * "sudo service  presence start" pour démarrer le service immédiatement