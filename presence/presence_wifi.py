#!/usr/bin/python3
# -*- coding: utf-8 -*-

# script requires:
# library scapy: pip install --user scapy
# sudo apt-get install tcpdump

from multiprocessing import Process
from scapy.all import * 
import datetime
import time

# Credentials
import sys
sys.path.append('/home/pi/domoticz/scripts/python/') # .. = dossier parent
from library_credentials import *


#########   Wifi   #########
macAddressesWifi = { "XX:XX:XX:XX:XX:XX" }


# ne marche pas avec MBP (car il se réveille tout seul de temps en temps)
# En pratique, je constate qu'un iPhone non utilisé envoie un paquet Ethernet toutes les 15 minutes et 15s maximum même s'il y a certains rares cas à +20min (testé en 02/2018) alors qu'un Android reste inactif en permanence


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
        #print(str(now) + " " + mac + " adresse mac source détectée")
        os.system('echo ' + str(now) + ' mac ' + mac + ' detectee >> /home/pi/domoticz/scripts/python/presence/testiphone.log') 

        

def initSniff():
    global lasttime, sniff_filters
    lasttime = datetime.datetime.now() - datetime.timedelta(days = 1) # On initialise la variable lasttime 
    sniff_filters = " or ".join(["ether src host " + mac for mac in macAddressesWifi]) 


def startSniff(iface = "eth0"):
    print("Sniffing started on %s ..." % iface)
    print(sniff(iface=iface, prn=mac_detect, filter=sniff_filters, store=0))



if __name__ == '__main__':

    initSniff()

    # déclaration des processus
    process_eth0 = Process(target=startSniff,  args=('eth0', ))
    process_mon0 = Process(target=startSniff,  args=('mon0', )) # ne marche pas avec iPhone

    # démarrage processus
    process_eth0.start()
    process_mon0.start()
    #print(process_eth0.pid)
    #print(process_mon0.pid)

    # Redémarrage des processus si besoin (jusqu'à N fois)
    i = 0
    while i < 100:

        if process_eth0.is_alive() == False:
            i = i + 1
            print("Restart sniffing on eth0")
            process_eth0.terminate()
            process_eth0.join()
            process_eth0 = Process(target=startSniff,  args=('eth0', ))
            process_eth0.start()
        
        if process_mon0.is_alive() == False:
            i = i + 1
            print("Restart sniffing on mon0")
            process_mon0.terminate()
            process_mon0.join()
            process_mon0 = Process(target=startSniff,  args=('mon0', ))
            process_mon0.start()
        
        time.sleep(60)

    # On termine tous les processus enfants après N tentatives
    process_mon0.terminate()
    process_mon0.join()
    process_eth0.terminate()
    process_eth0.join()

