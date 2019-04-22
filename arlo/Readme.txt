
Installation du script python pour qu’il s’exécute au démarrage du serveur :

1. sudo cp ./arlo_cmd /etc/init.d/
2. sudo chmod 755 /etc/init.d/arlo_cmd
3. sudo update-rc.d arlo_cmd defaults
   (sudo update-rc.d arlo_cmd remove => pour supprimer le démarrage auto du script)
   ("sudo service arlo_cmd start" pour démarrer le service immédiatement)