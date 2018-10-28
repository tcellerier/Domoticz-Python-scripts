#!/usr/bin/python3
# -*- coding: utf-8 -*-


#
# Script de mise à jour du system de caméra à partir d'un device Domoticz
# ( System temporaire en attendant le plugin plus adapté (pour le moment trop instable) )
#

import time
import sys
from pyarlo import PyArlo # Arlo Python library https://github.com/tchellomello/python-arlo



def arlo_switch(command, i = 0):
    
    try:
        arlo  = PyArlo(ArloLogin, ArloPassword)
        base = arlo.base_stations[0]  # get base station handle, assuming only 1 base station is available

        print("ARLO -- Command: " + command)

        if command == "status":
            print("ARLO -- Camera current mode: " + base.mode)

        elif command == "on":
            #print("ARLO -- Camera old mode: " + base.mode)
            base.mode = 'armed'
            time.sleep(1)
            print("ARLO -- Camera new mode: " + base.mode)

        else:
            #print("ARLO -- Camera old mode: " + base.mode)
            base.mode = 'disarmed'
            time.sleep(1)
            print("ARLO -- Camera new mode: " + base.mode)

    # On tente d'exécuter la commande 8 fois maximum
    except:
        if i < 8:
            print("ARLO -- Connexion Error - new try ... (" + str(i+1) + "/8)")
            arlo_switch(command, i+1)
        else:
            print("ARLO -- Connexion Errors -- command failed " + str(i) + " times. Exit")
            raise SystemExit(1) # Return failure


    #time.sleep(1)
    #print("ARLO -- Camera modes: " + str(base.available_modes))
    
    # Enregistre l'état de la batterie
    time.sleep(1)
    cam_battery_level = arlo.cameras[0].battery_level # de 0 à 100
    print("ARLO -- Camera Battery: " + str(cam_battery_level) + " % -> into file /tmp/arlo_cam1.txt")
    with open('/tmp/arlo_cam1.txt', 'w') as f:
        f.write(str(cam_battery_level)) 



if __name__ == "__main__":

    ################
    #  Parameters  #
    ################
    ArloLogin = "login@gmail.com"
    ArloPassword = "password"
    ################

    
    # Si pas d'argument
    if len(sys.argv) <= 1:
        arlo_switch("off")
    else:
        arlo_switch(sys.argv[1].lower())
    
