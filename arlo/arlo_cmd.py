#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Script de gestion des caméras Arlo


import time
import datetime
import sys
import os
from arlo import Arlo # Arlo Python library https://github.com/jeffreydwalter/arlo
# pip3 remove sseclient-py => si pb avec le script

sys.path.append('/home/pi/domoticz/scripts/python/') # .. = dossier parent
from library_credentials import *


# Retourne l'état de la caméra
def get_current_state(arlo):
    try:
        current_mode = arlo.GetModesV2()[0]['activeModes'][0]
        if current_mode == 'mode0':
            current_status = 'disarmed'
        elif current_mode == 'mode1':
            current_status = 'armed'
        else:
            current_status = current_mode
        return current_status

    except Exception as e:
        return 'Error'


# Fonction pour armer ou désarmer la caméra
def switch(command, i = 0):
    
    try:
        arlo = Arlo(ArloLogin, ArloPassword)
        base = arlo.GetDevices('basestation')[0]  # get base station info, assuming only 1 is available
        camera = arlo.GetDevices('camera')[0]  # get camera info, assuming only 1 is available

        print("Command: " + command)

        if command == "status":
            print("ARLO -- Camera current mode: " + get_current_state(arlo))

        elif command == "armed":
            #print("ARLO -- Camera old mode: " + get_current_state(arlo))
            arlo.Arm(base)
            print("ARLO -- Camera new mode: " + get_current_state(arlo))

        else:
            #print("ARLO -- Camera old mode: " + get_current_state(arlo))
            arlo.Disarm(base)
            print("ARLO -- Camera new mode: " + get_current_state(arlo))

    # On tente d'exécuter la commande 8 fois maximum
    except Exception as e:
        print(e)
        if i < 8:
            print("ARLO -- Connexion Error - new try ... (" + str(i+1) + "/8)")
            switch(command, i+1)
            return
        else:
            print("ARLO -- Connexion Errors -- command failed " + str(i) + " times. Exit")
            raise SystemExit(1) # Return failure

    # Enregistre l'état de la batterie (pour lecture dans Domoticz)
    time.sleep(1)
    cam_battery_level = arlo.GetCameraState(base)["properties"][0]["batteryLevel"]
    print("ARLO -- Camera Battery: " + str(cam_battery_level) + " % -> into file /tmp/arlo_cam1.txt")
    with open('/tmp/arlo_cam1.txt', 'w') as f:
        f.write(str(cam_battery_level)) 



# Fonction pour détecter les mouvements
def motion_detection():

    global nb_alert,time_lastalert
    nb_alert = 0
    time_lastalert = datetime.datetime.now() - datetime.timedelta(days = 1) # On initialise la variable time_lastalert à J-1
    print("ARLO - Motion detection (uniquement lorsque la caméra est armée)")
    while True:
        try:
            arlo = Arlo(ArloLogin, ArloPassword)
            base = arlo.GetDevices('basestation')[0]  # get base station info, assuming only 1 is available
            arlo.SubscribeToMotionEvents(base, motion_callback)
            #arlo.HandleEvents(base, motion_callback)
        
        except Exception as e:
            print(e)
            time.sleep(10) # Si erreur, on fait une pause de 10s



# callback function that will get called once per motion event
def motion_callback(arlo, event):

    global time_lastalert, nb_alert
    # Here you will have access to self, the basestation JSON object, and the event schema.
    print("Motion event detected!")
    print(event)

    now = datetime.datetime.now()
    delay_lastalert = (now - time_lastalert).total_seconds() # nombre de secondes.microsecondes
    time_lastalert = now

    if delay_lastalert > delay_alert: # On identifie de quelle détection à la suite il s'agit
        nb_alert = 1
    else:
        nb_alert = nb_alert+1

    # Si c'est la 1ere detection, on joue un scenario avec le son à fond
    if nb_alert == 1:
        print("1ere detection - message sonore")
        volume = os.popen('ssh root@' + nas_ip + ' "' + volume_path + ' -g"').read()
        os.system('ssh root@' + nas_ip + ' "' + volume_path + ' -s 100 && wget -q -U Mozilla -O /tmp/domoticz_tts.mp3 \'' + tts_api_url + 'Infraction détectée. Confirmez votre identitée avec votre téléphone dans les 20 secondes\' && ' + player_path + ' /tmp/domoticz_tts.mp3 && ' + volume_path + ' -s ' + volume + '" &')
    
    # Si c'est la 2è detection consécutive, on active l'alarme detecteur fumée
    elif nb_alert == 3:
        print("3e detection à la suite - activation alarme incendie & son alarme NAS")
        os.system('curl --user ' + domoticzCredentials + ' "http://127.0.0.1/json.htm?type=command&param=switchlight&idx=613&switchcmd=On" &')  # Alarme incendie
        volume = os.popen('ssh root@' + nas_ip + ' "' + volume_path + ' -g"').read()
        os.system('scp /home/pi/domoticz/scripts/python/arlo/domoticz_alarm.mp3 root@' + nas_ip + ':/tmp/domoticz_alarm.mp3 && ssh root@' + nas_ip + ' "' + volume_path + ' -s 100 && ' + player_path + ' /tmp/domoticz_alarm.mp3 && ' + volume_path + ' -s ' + volume + '" &')          # alarme sur haut parleur
    
    # Si c'est la 4e détection consécutive
    elif nb_alert == 4:
        print("4e detection à la suite")
    



if __name__ == "__main__":

    ################
    #  Parameters  #
    ################
    ArloLogin = "abc@gmail.com" # 2e compte avec droits limités
    ArloPassword = "XXXX"

    # Synology NAS pour USB speakers
    nas_ip = "192.168.99.4"
    tts_api_url = "http://api.voicerss.org/?key=XXXXX&f=44khz_16bit_mono&c=MP3&hl=fr-fr&src="
    player_path = "/var/packages/AudioStation/target/bin/mplayer"
    volume_path = "/var/packages/AudioStation/target/bin/volume"

    delay_alert = 500    # delai maximum en secondes pour considerer que 2 alertes sont consécutives
    ################

    # Si pas d'argument, on désarme la caméra
    if len(sys.argv) <= 1:
        switch("disarmed")
    elif sys.argv[1].lower() == 'motion':
        motion_detection()
    # sinon on exécute le mode swtich
    else:
        switch(sys.argv[1].lower())



    
