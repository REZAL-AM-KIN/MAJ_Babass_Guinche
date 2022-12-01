# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:48:43 2022

@author: Lenovo X1
"""
import paramiko as prk
import os
import requests
import zipfile
import sys
import tempfile
    
def getBabasList(online=True):
    try:
        r= requests.get("http://192.168.1.101:5574/rezalajax")
    except ConnectionError:
        print("Connexion error")
        sys.exit()
    babas=r.json()["data"]
    return [[b[0],b[1],b[-1]] for b in babas if b[2]==online]


def checkUpdateFile(filePath):
    with zipfile.ZipFile(filePath, 'r') as zipObj:
        listOfiles = zipObj.namelist()
        if (not "PICONFLEX2000-CLIENT/" in listOfiles):
            return False
    return True

def updateSettingsFile(zipFilePath, boxId):
    
        # generate a temp file
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    
    # create a temp copy of the archive without filename            
    with zipfile.ZipFile(zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            
            listOfiles = zin.namelist()
            
            if not ("PICONFLEX2000-CLIENT/setting.py" in listOfiles):
                print("No settings update.")
                for item in zin.infolist():
                    zout.writestr(item, zin.read(item.filename))
                return tmpname
            
            s=zin.read("PICONFLEX2000-CLIENT/setting.py").decode()
            for item in zin.infolist():
                if item.filename != "PICONFLEX2000-CLIENT/setting.py":
                    zout.writestr(item, zin.read(item.filename))

    
    
    if not "numeroBox=" in s.replace(" ",""):
        print("Erreur, constante numeroBox absente du fichier setting.py")
        sys.exit()
    p=s.split("numeroBox =")
    p[0]+="numeroBox="
    d=p[1].split("\n")
    d[0]=str(boxId)
    p[1]="\n".join(d)
    s="".join(p)

    # now add filename with its new data
    with zipfile.ZipFile(tmpname, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("PICONFLEX2000-CLIENT/setting.py", s.encode())
        
    return tmpname

def updatePrg(ip, boxId, updatePath):
    s="exec(open(\'/home/pi/PICONFLEX2000-CLIENT/launch.py\').read()) \nhint('Updating', 2)"
    
    print("Update setting file to match boxId : "+str(boxId))
    zipFilePath = updateSettingsFile(updatePath, boxId)
    
    ssh = prk.SSHClient() 
    ssh.set_missing_host_key_policy(prk.AutoAddPolicy)
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    print("Connection to "+ip)
    try:
        ssh.connect(ip, username="pi", password="pi")
        print("Connection established.")
    except Exception:
        print("Connection error, exiting")
        sys.exit() 
    
    print("Set update mode")
    stdin, stdout, stderr = ssh.exec_command("echo \""+s+"\" > update.py")
    stdin, stdout, stderr = ssh.exec_command("python3 update.py")
    print(stderr.read())
    stdin, stdout, stderr = ssh.exec_command("rm update.py")
       
    """
    print("Cleaning old files")
    stdin, stdout, stderr = ssh.exec_command("sudo -k rm -r ~/PICONFLEX2000-CLIENT")
    if ("password".encode('utf-8') in stdout.read()):
        stdin.write("pi\n")
        stdin.flush()
        
    stdin, stdout, stderr = ssh.exec_command("sudo -k rm -r ~/PICONFLEX2000-FONCTIONS")
    if ("password".encode('utf-8') in stdout.read()):
        stdin.write("pi\n")
        stdin.flush()
    """
        
    stdin, stdout, stderr = ssh.exec_command("rm update.zip")
        
    print("Clean succeed")
    
    sftp = ssh.open_sftp()
    print("Sending update")
    sftp.put(zipFilePath, "update.zip")
    print("Upload completed")
    sftp.close()
    
    print("Unzipping")
    stdin, stdout, stderr = ssh.exec_command("unzip -o ~/update.zip")
    if stderr.read() != "".encode():
        print(stderr.read().decode())
        print("Unzip fail")
    else:
        print("Unzip completed")
    print("Update completed")
    
    
    print("Rebooting")
    stdin, stdout, stderr = ssh.exec_command("sudo -k reboot")
    if ("password".encode('utf-8') in stdout.read()):
        stdin.write("pi\n")
        stdin.flush()
    ssh.close()
    os.remove(zipFilePath)
    
def removeLog(ip):
    ssh = prk.SSHClient() 
    ssh.set_missing_host_key_policy(prk.AutoAddPolicy)
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    print("Connection to "+ip)
    try:
        ssh.connect(ip, username="pi", password="pi")
        print("Connection established.")
    except Exception:
        print("Connection error, exiting")
        sys.exit() 
        
    print("Deleting logs of "+ip)
    stdin, stdout, stderr = ssh.exec_command("sudo -k rm -r ~/PICONFLEX2000-LOGS")
    if ("password".encode('utf-8') in stdout.read()):
        stdin.write("pi\n")
        stdin.flush()
    ssh.close()
    
def removeAllLog():
    for b in getBabasList():
        removeLog(b[2])
        
def command(ip,cmds):
    ssh = prk.SSHClient() 
    ssh.set_missing_host_key_policy(prk.AutoAddPolicy)
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    print("Connection to "+ip)
    try:
        ssh.connect(ip, username="pi", password="pi")
        print("Connection established.")
    except Exception:
        print("Connection error, exiting")
        sys.exit() 
        
    for c in cmds:
        stdin, stdout, stderr = ssh.exec_command(c)
        if ("password".encode('utf-8') in stdout.read()):
            stdin.write("pi\n")
            stdin.flush()
    ssh.close()
    
def sendCommandtoAll(cmds):
    for b in getBabasList():
        command(b[2],cmds)

def poweroff(boxId):
    onlineBabasDic = {b[1]:b[2] for b in getBabasList()}
    command(onlineBabasDic[boxId],["sudo poweroff"])

def reboot(boxId):
    onlineBabasDic = {b[1]:b[2] for b in getBabasList()}
    command(onlineBabasDic[boxId],["sudo reboot"])
    
def poweroffAll():
   sendCommandtoAll(["sudo poweroff"])   
    
def rebootAll():
    for b in getBabasList():
        command(b[2],["sudo reboot"])
        
def stopServers():
    command("192.168.1.101",["sudo poweroff"])
    command("192.168.1.100",["sudo poweroff"])

def update():
    print("Babas hors ligne:\n")
    offlineBabas = getBabasList(False)
    for b in offlineBabas:
        print(str(b[1])+"|"+str(b[0])+"|"+str(b[2]))
    
    print("\n\nBabas en ligne:\n")
    onlineBabas = getBabasList()
    for b in onlineBabas:
        print(str(b[1])+"|"+str(b[0])+"|"+str(b[2]))
    print("\n\n Il y a "+str(len(onlineBabas))+" babas en ligne et "+ str(len(offlineBabas))+" babas hors ligne.")
    print("Voulez vous faire la mise à jour de toutes les baba's en ligne ?")
    
    choice = -1
    while choice == -1:
    	print("Voulez vous faire la mise à jour de toutes les baba's en ligne ?")
    	print("     1- Mise à jour générale\n     2- Mise à jour des babas spécifiées\n     3- Quitter")
    	entry = input("Votre choix ? ")
    	if not (entry in "123" ) or len(entry) != 1:
    		print("Saisie invalide.Vous devez entrer un chiffre entre 1 et 3")
    		continue
    	choice = int(entry)
        
    if (choice == 3):
        sys.exit()
    else:
        filePath = None
        while filePath == None:
            print("Entrez un chemin vers le fichier de mise à jour (Fichier zip contenant PICONFLEX2000-CLIENT et PICONFLEX2000-FONCTIONS)")
            entry = input("Chemin : ")
            if not zipfile.is_zipfile(entry):
                print("Fichier zip invalide\n\n")
                continue
            if not checkUpdateFile(entry):
                print("La structure de fichier de mise à jour n'est pas respectée (dossier PICONFLEX2000- manquant)\n\n")
                continue
            filePath=entry
    
    if (choice == 1):
        entry = input("Confirmer mise à jour générale avec le code 8214:")
        if not entry=="8214":
            print("Sortie")
            return
  
        for b in getBabasList():
            updatePrg(b[2],b[1],filePath)
    
    if (choice == 2):
        onlineBabasDic = {b[1]:b[2] for b in getBabasList()}
        babas = {}
        while len(babas) == 0:
            entry = input("Numéro des babas séparé par des espaces: ")
            valid = True
            for e in entry.split(" "):
                if not e.isdigit():
                    valid = False
                    break
                if not int(e) in onlineBabasDic.keys():
                    valid = False
                    break
                babas[int(e)]=onlineBabasDic[int(e)]
            if not valid:
                babas={}
                continue
        print("Babas à mettre à jour: "+str(babas))
        entry = input("Confirmer mise à jour générale avec le code 8214:")
        if not entry=="8214":
            print("Sortie")
            return
  
        for id,ip in babas.items():
            updatePrg(ip,id,filePath)

            
