#!/usr/bin/python
# -*- coding: utf-8 -*-

# script requires:
# library scapy: pip install --user scapy
# sudo apt-get install tcpdump

from scapy.all import * 
import datetime

# Credentials
import sys
sys.path.append('/home/pi/domoticz/scripts/python/') # .. = dossier parent
from library_credentials import *


# Liste des adresses MAC dont on va tester la présence
macAddresses = { "XX:XX:XX:XX:XX:XX" }


def mac_detect(pkt):

    global lasttime

    # Show all the packet
    # print(pkt.show()) 

    # Lecture de l'adresse mac dans le paquet
    mac = ""
    if pkt.haslayer(Ether):
        mac = pkt[Ether].src
    elif  pkt.haslayer(Dot11): # Layer 802.11
        mac = pkt[Dot11].addr2

    if mac == "":
        return

    now = datetime.datetime.now()
    min_delay = 30    # delai minimum en secondes pour la prise en compte d'un nouveau paquet
  
    # On sort du script si on n'est pas dans la tranche horaire 8h - 23h59
    #if not now.hour >= 8:
    #    return
    
    
    delay_lastpush = (now - lasttime).total_seconds() # nombre de secondes.microsecondes

    if delay_lastpush >= min_delay:
        lasttime = now
        
        ###  Actions à déclencher  ###
        #print str(now) + " " + mac + " adresse mac source détectée"
        os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=updateuservariable&vname=Script_Presence_Maison&vtype=0&vvalue=1" &') 
    


def initSniff():
    global lasttime, sniff_filters
    lasttime = datetime.datetime.now() - datetime.timedelta(days = 1) # On initialise la variable lasttime 
    sniff_filters = " or ".join(["ether src host " + mac for mac in macAddressesWifi]) 


def startSniff(iface = "eth0"):
    #lasttime = vlasttime.value
    print("Sniffing started on %s ..." % iface)
    print(sniff(iface=iface, prn=mac_detect, filter=sniff_filters, store=0))


if __name__ == '__main__':

    initSniff()

    Process(target=startSniff,  args=('eth0', )).start()
    Process(target=startSniff,  args=('mon0', )).start()
