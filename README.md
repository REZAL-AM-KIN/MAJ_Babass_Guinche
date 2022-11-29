# MAJ_Babass_Guinche
Script pour la mise à jour des baba'ss.


# Necessite :
 - L'ordinateur exécutant le script doit être connecter 
 - Le serveur doit être démarré (permet au script de récupérer les id de baba'ss en ligne
 - La lib paramiko sur l'ordi qui executre le script

# Utilisation
Le script permet la mise à jour de chaque baba'ss à partir d'un fichier zip contenant les dossiers CLIENT et FONCTIONS
Note : le scripte change tout seul le numéro de baba'ss pour chaque baba'ss en cas d'update du fichier CLIENT/settings.py
il s'agit d'un receuil de fonction. Il faut donc importer ou executer le fichier pour pouvoir les utiliser.
Les fonctions disponibles sont :
- ``` getBabasList(online=True) ``` --> renvoi la liste des baba'ss
- ``` removeLog(ip) ``` --> Supprime les logs ( automatiquement executer lors de la mise à jour du script)
- ``` removeAllLog() ``` --> Supprime les logs de toutes les baba'ss
- ``` command(ip, cmds) ``` --> Execute les commandes [cmds] sur la baba'ss [ip] 
- ``` sendCommandtoAll(cmds) ``` --> Execute les commandes [cmds] sur toutes les baba'ss
- ``` poweroff(boxId) ``` --> Eteint la baba'ss [boxId]
- ``` reboot(boxId) ``` --> Reboot la baba'ss [boxId]
- ``` poweroffAll() ``` -->
- ``` rebootAll() ``` --> Reboot toutes les baba'ss
- ``` stopServers() ``` --> Eteint proprement les serveurs
- ``` update() ``` --> Lance le programme d'update automatique. On suit ensuite les instructions proposées

Pour une update guidé executer ``` update() ``` puis suivre les informations.
NOTE: Le fichier compressé doit être un zip qui contient les dossiers PICONFLEX2000-CLIENT et PICONFLEX2000-FONCTIONS
