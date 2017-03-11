
Installation du script python pour qu’il s’exécute au démarrage du serveur :

1. sudo cp ./presence /etc/init.d/
2. sudo chmod 755 /etc/init.d/presence
3. sudo update-rc.d presence defaults
   (sudo update-rc.d presence remove => pour supprimer le démarrage auto du script)
   ("sudo service  presence start" pour démarrer le service immédiatement)
