#!/usr/bin/python
# -*- coding: utf-8 -*-


#
# Script de mise à jour du system de caméra à partir d'un device Domoticz
# ( System temporaire en attendant le plugin plus adapté (pour le moment trop instable) )
#

import time
import sys
from pyarlo import PyArlo # Arlo Python library 



def arlo_switch(command, i = 0):
    
    try:
        arlo  = PyArlo(ArloLogin, ArloPassword)
        time.sleep(1)
        base = arlo.base_stations[0]  # get base station handle, assuming only 1 base station is available
        time.sleep(1)

        print("ARLO -- Command: " + command)

        if command == "status":
            print("ARLO -- Camera current mode: " + base.mode)

        elif command == "on":
            print("ARLO -- Camera old mode: " + base.mode)
            base.mode = 'armed'
            time.sleep(1)
            print("ARLO -- Camera new mode: " + base.mode)

        else:
            print("ARLO -- Camera old mode: " + base.mode)
            base.mode = 'disarmed'
            time.sleep(1)
            print("ARLO -- Camera new mode: " + base.mode)

        time.sleep(1)
        print("ARLO -- Camera modes: " + str(base.available_modes))
        
        #time.sleep(1)
        #cam_battery = arlo.cameras[0].get_battery_level
        #print("ARLO -- Camera Battery: " + str(cam_battery) + " %")

    # On tente d'exécuter la commande 5 fois maximum
    except:
        if i < 5:
            print("ARLO -- Connexion Error - new try ... (" + str(i+1) + "/5)")
            arlo_switch(command, i+1)
        else:
            print("ARLO -- Connexion Error -- command failed. Exit")
            raise SystemExit(1) # Return failure



if __name__ == "__main__":

    ################
    #  Parameters  #
    ################
    ArloLogin = "login@gmail.com"
    ArloPassword = "password"
    ################

    
    # Si pas d'arugment
    if len(sys.argv) <= 1:
        arlo_switch("off")
    else:
        arlo_switch(sys.argv[1].lower())
    
