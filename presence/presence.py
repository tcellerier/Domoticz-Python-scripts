#!/usr/bin/python3
# -*- coding: utf-8 -*-

# script requires:
# library scapy: pip install --user scapy
# sudo apt-get install tcpdump
# bluetooth: sudo pip3 install pybluez && sudo apt-get install python-bluez

from multiprocessing import Process,Value
from scapy.all import *
import bluetooth  
import datetime
import time


macAddressesWifi = {"XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX"}
macAddressesBluetooth = {"XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX"}


# Le check Wifi ne marche pas avec MBP (car il se réveille tout seul de temps en temps)
# En pratique, je constate qu'un iPhone non utilisé envoie un paquet Ethernet toutes les 15 minutes et 15s maximum même s'il y a certains rares cas à +20min (testé en 02/2018) alors qu'un Android reste inactif en permanence



# Action déclenchée quand une présence est détectée
def ActionPresence():
    now = datetime.datetime.now()
    min_delay = 60    # delai minimum en secondes pour la prise en compte d'un nouveau paquet
  
    # On sort du script si on n'est pas dans la tranche horaire 8h - 23h59
    #if not now.hour >= 8:
    #    return

    if now.timestamp() - LastTimestampShared.value >= min_delay:
        LastTimestampShared.value = math.floor(now.timestamp())
        ###  Actions à déclencher  ###
        #print(now)
        #os.system('echo ' + str(now) + ' mac ' + mac + ' detectee >> /home/pi/domoticz/scripts/python/presence/testiphone.log')

    

# Process de présence Wifi
def WifiStartSniff(LastTimestampShared, iface = "eth0"):
    #global LastTimestampShared
    print("Sniffing started on %s ..." % iface)
    WifiSniffFilters = " or ".join(["ether src host " + mac for mac in macAddressesWifi]) 
    print(sniff(iface=iface, prn=WifiDetectMAC, filter=WifiSniffFilters, store=0))
    return

# Function called when a Wifi packet is sniffed
def WifiDetectMAC(pkt):
    # print(pkt.show()) # show all the packets
    mac = ""
    if pkt.haslayer(Ether):
        mac = pkt[Ether].src # Lecture de l'adresse mac dans le paquet
    elif pkt.haslayer(Dot11): # Layer 802.11
        mac = pkt[Dot11].addr2
    if mac == "":
        return
    #print("Presence Wifi %s" % mac)
    ActionPresence()
    
# Process de présence Bluetooth
def BTStartPing(LastTimestampShared):
    print("Bluetooth Ping started")
    while True:
        for device in macAddressesBluetooth:
            try:
                ret = bluetooth.lookup_name(device, timeout=5)
                if ret:
                    #print("Presence BT %s %s" % (device, ret))
                    ActionPresence()
            except:
                return    
        time.sleep(14*60) # Sleep 14 min



if __name__ == '__main__':

    # On initialise les variables
    LastTimestamp = math.floor(datetime.datetime.now().timestamp() - 3600) # initialisé à -1h
    LastTimestampShared = Value('i', LastTimestamp) # Shared variable between sub processes

    # déclaration des processus
    process_wifi_eth0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'eth0'))
    process_wifi_mon0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'mon0')) # Ecoute en mode Monitor sur tous les canaux. Ne marche pas avec l'iPhone s'il n'est pas connecté à un Wifi afin de révéler son adresse MAC réelle
    process_bt = Process(target=BTStartPing, args=(LastTimestampShared,))

    # démarrage processus
    process_wifi_eth0.start()
    process_wifi_mon0.start()
    process_bt.start()


    # Redémarrage des processus si besoin
    while True:
        time.sleep(43200) # Wait 12h 
        if process_wifi_eth0.is_alive() == False:
            print("Restart sniffing on eth0")
            process_wifi_eth0.terminate()
            time.sleep(1)
            process_wifi_eth0.join()
            process_wifi_eth0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'eth0'))
            process_wifi_eth0.start()
        if process_wifi_mon0.is_alive() == False:
            print("Restart sniffing on mon0")
            process_wifi_mon0.terminate()
            time.sleep(1)
            process_wifi_mon0.join()
            process_wifi_mon0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'mon0'))
            process_wifi_mon0.start()
        if process_bt.is_alive() == False:
            print("Restart Bluetooth ping")
            process_bt.terminate()
            time.sleep(1)
            process_bt.join()
            process_bt = Process(target=BTStartPing, args=(LastTimestampShared,))
            process_bt.start()
        
