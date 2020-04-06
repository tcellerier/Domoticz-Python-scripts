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



MacAddressesWifi = ["XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX"]
MacAddressesBluetooth = ["XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX", "XX:XX:XX:XX:XX:XX"] # L'ordre est important, on ping d'abord le 1er de la liste, puis le 2e, etc.


# Le check Wifi ne marche pas avec MBP (car il se réveille tout seul de temps en temps)
# En pratique, je constate qu'un iPhone non utilisé envoie un paquet Wifi toutes les 15 minutes et 15s maximum même s'il y a certains rares cas à +20min (testé en 02/2018) alors qu'un Android reste inactif en permanence



# Action déclenchée quand une présence est détectée
def ActionPresence():
    now = datetime.datetime.now()
    min_delay = 60    # delai minimum en secondes pour la prise en compte d'un nouvel évènement de présence
  
    # On sort du script si on n'est pas dans la tranche horaire 8h - 23h59
    #if not now.hour >= 8:
    #    return

    if now.timestamp() - LastTimestampShared.value >= min_delay:
        LastTimestampShared.value = math.floor(now.timestamp())
        ###  Actions à déclencher  ###
        #print(now)
        #os.system('echo ' + str(now) + ' detectee >> /home/pi/domoticz/scripts/python/presence/testiphone.log')
        #os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=updateuservariable&vname=Script_Presence_Maison&vtype=0&vvalue=1" &') 
        os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=switchlight&idx=1040&switchcmd=On" &') 
    return

# Process de présence Wifi
def WifiStartSniff(LastTimestampShared, iface = "eth0"):
    print("Sniffing started on %s ..." % iface)
    WifiSniffFilters = " or ".join(["ether src host " + mac for mac in MacAddressesWifi]) 
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
    #print("------------ Presence Wifi %s ---" % mac)
    ActionPresence()
    return


# Process de présence Bluetooth - Ping les appareils uniquement si pas de présence détectée
def BTStartPing(LastTimestampShared):

    min_delay_bt = 720    # delai minimum en secondes entre un nouveau ping Bluetooth et le moment de dernière présence 

    print("Bluetooth Ping started")
    while True:
        now = datetime.datetime.now()
        if now.hour >= 1 and now.hour < 8: # On ne ping pas entre 1h et 8h du matin
            time.sleep(599)
            continue

        if now.timestamp() - LastTimestampShared.value >= min_delay_bt:
            for device in MacAddressesBluetooth:
                try:
                    ret = bluetooth.lookup_name(device, timeout=5)
                    if ret:
                        #print("------------ Presence BT détectée %s %s" % (device, ret))
                        ActionPresence()
                        break # On arrête de pinger si un des périphériques a répondu présent
                except:
                    return

        if now.timestamp() - LastTimestampShared.value + 10 >= min_delay_bt: # Si pas de présence, on retente toutes les "délai" secondes 
            sleep = min_delay_bt
        else:
            sleep =  min_delay_bt - (now.timestamp() - LastTimestampShared.value)   # Sinon si présence, on retente dans une durée complémentaire au délai total 
        time.sleep(sleep) 
    return



if __name__ == '__main__':

    # On initialise les variables
    LastTimestamp = math.floor(datetime.datetime.now().timestamp() - 3600) # initialisé à -1h
    LastTimestampShared = Value('i', LastTimestamp) # Shared variable between sub processes

    # déclaration des processus
    process_wifi_eth0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'eth0'))
    process_wifi_mon0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'mon0')) # Ecoute en mode Monitor sur tous les canaux. Ne marche pas avec l'iPhone s'il n'est pas connecté à un Wifi (afin de révéler son adresse MAC réelle)
    process_bt = Process(target=BTStartPing, args=(LastTimestampShared,))

    # démarrage processus
    process_wifi_eth0.start()
    process_wifi_mon0.start()
    process_bt.start()


    # Redémarrage des processus si besoin
    while True:
        time.sleep(14400) # Wait 4h 
        if process_wifi_eth0.is_alive() == False:
            print("Restart sniffing on eth0")
            process_wifi_eth0.terminate()
            time.sleep(2)
            process_wifi_eth0.join()
            process_wifi_eth0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'eth0'))
            process_wifi_eth0.start()
        if process_wifi_mon0.is_alive() == False:
            print("Restart sniffing on mon0")
            process_wifi_mon0.terminate()
            time.sleep(2)
            process_wifi_mon0.join()
            process_wifi_mon0 = Process(target=WifiStartSniff, args=(LastTimestampShared, 'mon0'))
            process_wifi_mon0.start()
        if process_bt.is_alive() == False:
            print("Restart Bluetooth ping")
            process_bt.terminate()
            time.sleep(2)
            process_bt.join()
            process_bt = Process(target=BTStartPing, args=(LastTimestampShared,))
            process_bt.start()
        

