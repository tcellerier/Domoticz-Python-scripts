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

    if not pkt.haslayer(Ether):
        return

    now = datetime.datetime.now()

    # On sort du script si on n'est pas dans la tranche horaire 10h - minuit
    if not now.hour >= 10:
        return

    min_delay = 60    # delai minimum en secondes pour la prise en compte d'un nouveau paquet
    
    mac = pkt[Ether].src
    delay_lastpush = (now - lasttime).total_seconds() # nombre de secondes.microsecondes

    if delay_lastpush >= min_delay:
        lasttime = now
        
        ###  Actions à déclencher  ###
        #print str(now) + " " + mac + " adresse mac source détectée"
        os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=updateuservariable&vname=Script_Presence_Maison&vtype=0&vvalue=1" &') 
    


def startSniff():

    global lasttime
    lasttime = datetime.datetime.now() - datetime.timedelta(days = 1) # On initialise la variable lasttime 

    sniff_filters = " or ".join(["ether src host " + mac for mac in macAddresses]) 
    print "Sniffing started"
    print(sniff(prn=mac_detect, filter=sniff_filters, store=0))



if __name__ == '__main__':
    startSniff()


