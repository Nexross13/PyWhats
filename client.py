import base64
import json
import os
import socket
import threading
import time

dataUser = []

def ConnexionServer():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))
    return client

def Login(client):
    type  = "login"
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    data = {'type': type, 'username': username, 'password': password}
    data = json.dumps(data)
    if SendToSocket(client, data) == "OK":
        dataUser.append((username, password))
        return True
    else:
        return False

def Register(client):
    type = "register"
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    data = {'type': type, 'username': username, 'password': password}
    data = json.dumps(data)
    if SendToSocket(client, data) == "OK":
        dataUser.append((username, password))
        return True
    else:
        return False

def SendMessage(client, sender, recipient):
    threading.Thread(target=ReceiveMessage, args=(client,)).start()
    while True:
        message = input("Message: ")
        if message == "exit":
            break
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{timestamp}] You : {message}")
        data = {'type': 'message', 'sender': sender, 'recipient': recipient, 'message': message, 'time': timestamp}
        SendToSocket(client, json.dumps(data))

def SendFile(client, sender, recipient):
    filename = ''
    extension = ''

    while True:
        file = input("Entrez le nom du fichier (exit pour quitter): ")
        if file == 'exit':
            return

        for i in range(len(file)):
            if file[i] == '.':
                extension = file[i:]
                break
            else :
                filename += file[i]
        
        if extension is None:
            extension = '.notxt'
        
        try:
            match extension:
                case '.txt':
                    with open(file, 'r') as file:
                        content = file.read(10000000)
                    break
                
                case '.notxt':
                    with open(file, 'r') as file:
                        content = file.read(10000000)
                    break

                case '.png':
                    with open(file, 'rb') as file:
                        content = file.read(10000000)
                        content = base64.b64encode(content).decode()
                    break

                case '.jpg':
                    with open(file, 'rb') as file:
                        content = file.read(10000000)
                        content = base64.b64encode(content).decode()
                    break

                case '.jpeg':
                    with open(file, 'rb') as file:
                        content = file.read(10000000)
                        content = base64.b64encode(content).decode()
                    break

                case '.pdf':
                    with open(file, 'rb') as file:
                        content = file.read(10000000)
                        content = base64.b64encode(content).decode()
                    break

                case _:
                    with open(file, 'r') as file:
                        content = file.read(10000000)
                    break

        except FileNotFoundError:
            filename = ''
            return "Fichier introuvable. Veuillez réessayer."
    
    data = {'type': 'file', 'sender': sender, 'recipient': recipient, 'filename': filename, 'extension':extension, 'content': content}

    return SendToSocket(client, json.dumps(data))

def SendToSocket(client, data):
    client.send(data.encode())
    return  ReceiveSocket(client)

def IsConnected(client, recipient):
    type = "is_connected"
    data = {'type': type, 'recipient': recipient}
    data = json.dumps(data)
    if SendToSocket(client, data) == "OK":
        return True
    else:
        return False
    
def ReceiveMessage(client):
    while True:
        data = ReceiveSocket(client)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{timestamp}] {data['sender']} : {data['message']}")
        
def ReceiveSocket(client):
    data = client.recv(1024).decode()
    # si data est de type json alors on le load
    try:
        data = json.loads(data)
        return data
    except:
        return data

def FirstMenu():
    client = ConnexionServer()

    print(" _____         __          __ _             _         ")
    print("|  __ \        \ \        / /| |           | |        ")
    print("| |__) | _   _  \ \  /\  / / | |__    __ _ | |_  ___  ")
    print("|  ___/ | | | |  \ \/  \/ /  | '_ \  / _` || __|/ __| ")
    print("| |     | |_| |   \  /\  /   | | | || (_| || |_ \__ \ ")
    print("|_|      \__, |    \/  \/    |_| |_| \__,_| \__||___/ ")
    print("          __/ |                                       ")
    print("         |___/                                        ")
    print("------------------------------------------------------")
    print("1. Se connecter")
    print("2. S'inscrire")
    print("3. Quitter")
    while True:
        choice = input("Votre choix: ")
        match choice:
            case "1":
                login = Login(client)
                print(login)
                if login == True:
                    print("Connexion...")
                    SecondMenu(client)
                else:
                    print("Nom d'utilisateur ou mot de passe incorrect")

            case "2":
                register = Register(client)
                if register == True:
                    print("Connexion...")
                    SecondMenu(client)
                else:
                    print("Nom d'utilisateur déjà utilisé")

            case "3":
                break

            case _:
                print("Choix invalide")

def SecondMenu(client):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" ____   _                                                ")
    print("|  _ \ (_)                                               ")
    print("| |_) | _   ___  _ __  __   __  ___  _ __   _   _   ___  ")
    print("|  _ < | | / _ \| '_ \ \ \ / / / _ \| '_ \ | | | | / _ \ ")
    print("| |_) || ||  __/| | | | \ V / |  __/| | | || |_| ||  __/ ")
    print("|____/ |_| \___||_| |_|  \_/   \___||_| |_| \__,_| \___| ")
    print("---------------------------------------------------------")

    # Menu après authentification
    while True:
        print("\nMenu :")
        print("1. Envoyer un message")
        print("2. Envoyer un fichier")
        print("3. Voir qui est connecté")
        print("4. Modifier son profil")
        print("5. Se déconnecter")
        choix = input("Que souhaitez-vous faire? (Entrez le numéro de l'option) : ")
        os.system('cls' if os.name == 'nt' else 'clear')

        match choix :
            case '1':
                recipient = input("Destinataire: ")
                if  IsConnected(client, recipient) == False:
                    print(f"{recipient} n'est pas connecté")
                else:
                    ChatRoom(client, recipient)

            case '2':
                recipient = input("Destinataire: ")
                if IsConnected(client, recipient) == "False":
                    print(f"{recipient}  n'est pas connecté")
                else:
                    SendFile(client, dataUser[0], recipient)

            case '3':
                data = {'type': 'connected'}
                print(SendToSocket(client, data))

            case '4':
                print(UpdateProfileMenu(client))

            case '5':
                data = {'type': 'logout', 'sender': dataUser[0]}
                print(SendToSocket(client, data))
                break

            case _:
                print("Choix invalide. Veuillez réessayer.")

def ChatRoom(client, recipient):
    print("Chatroom avec " + recipient)
    SendMessage(client, dataUser[0], recipient)

def UpdateProfileMenu(client):
    print("1. Modifier son nom d'utilisateur")
    print("2. Modifier son mot de passe")
    print("3. Retour")
    while True:
        choice = input("Votre choix: ")
        match choice:
            case "1":
                newUsername = input("Nouveau nom d'utilisateur: ")
                data = {'type': 'update_username', 'username': dataUser[0], 'newUsername': newUsername}
                if SendToSocket(client, data) == "OK":
                    dataUser[0] = newUsername
                    return "Nom d'utilisateur modifié"
                
                else:
                    return "Nom d'utilisateur déjà utilisé"

            case "2":
                newPassword = input("Nouveau mot de passe: ")
                data = {'type': 'update_password', 'username': dataUser[0], 'newPassword': newPassword}
                if SendToSocket(client, data) == "OK":
                    dataUser[0] = newUsername
                    return "Password modifié"

            case "3":
                return

            case _:
                print("Choix invalide")

def Main():
    FirstMenu()

if __name__ == '__main__':
    Main()