#!/usr/bin/python
# -*- coding: utf-8 -*-

# script requires:
# library scapy: pip install --user scapy
# sudo apt-get install tcpdump

from scapy.all import * 
from datetime import datetime

# Credentials
import sys
sys.path.append('/home/pi/domoticz/scripts/python/') # .. = dossier parent
from library_credentials import *



# iPhone 6S CC:20:E8:C7:5B:E7
# Sony Nedra 
# MBP 20:c9:d0:44:ad:99

# Liste des adresses MAC dont on va tester la présence
macAddresses = { "CC:20:E8:C7:5B:E7" }


def mac_detect(pkt):
   
    if not pkt.haslayer(Ether):
        return

    min_delay = 60    # delai minimum en secondes pour la prise en compte d'un nouveau paquet
    now = datetime.now()
    mac = pkt[Ether].src
    if not (mac in lasttime):   # 1ere fois que l'adresse MAC est détectée
        delay_lastpush = 999
    else:
        delay_lastpush = (now - lasttime[mac]).total_seconds() # nombre de secondes.microsecondes


    if delay_lastpush >= min_delay:
        lasttime[mac] = now
        
        # Actions à déclencher
        #print str(now) + " " + mac + " adresse mac source détectée"
        os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=updateuservariable&vname=Script_Presence_Maison&vtype=0&vvalue=1" &') 
    


def startSniff():

    global lasttime
    lasttime = {}

    sniff_filters = " or ".join(["ether src host " + mac for mac in macAddresses]) 
    print "Sniffing started"
    print(sniff(prn=mac_detect, filter=sniff_filters, store=0))



if __name__ == '__main__':
    startSniff()


