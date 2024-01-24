from asyncio import sleep
import base64
import os
import socket
import json
import threading
import time

def update_profile(username):
    print("\nMenu :")
    print("1. Modifier le nom d'utilisateur")
    print("2. Modifier le mot de passe")
    print("3. exit")
    choix = input("Que souhaitez-vous faire? (Entrez le numéro de l'option) : ")
    match choix :
        case '1':
            new_username = input("Entrez le nouveau nom d'utilisateur : ")
            data = {'type': 'update', 'code': 'username', 'sender': username, 'new_username': new_username}
            client.send(json.dumps(data).encode())
            return new_username 
        
        case '2':
            new_password = input("Entrez le nouveau mot de passe : ")
            data = {'type': 'update', 'code': 'password', 'sender': username, 'password': new_password}
            client.send(json.dumps(data).encode())
            return "Null"
        
        case '3':
            print('')

        case _:
            print("Choix invalide. Veuillez réessayer.")

def send_file(username):
    recipient = input("Entrez le destinataire : ")
    sender = username
    filename = ''
    while True:
        file = input("Entrez le nom du fichier : ")
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
            print("Fichier introuvable. Veuillez réessayer.")
    
    data = {'type': 'file', 'sender': sender, 'recipient': recipient, 'filename': filename, 'extension':extension, 'content': content}

    client.send(json.dumps(data).encode())

    print("Fichier envoyé")

def receive_file(data):
    # Première étape: le client reçoit les données du fichier
    print("Fichier en cours de transfert...")
    # Deuxième étape: le client enregistre les données du fichier
    filename = data['filename']
    extension = data['extension']
    content = data['content']

    if extension == '.notxt':
        file = filename
    else:
        file = filename + extension

    match extension:
        case '.txt':
            with open(file, 'w') as f:
                f.write(content)

        case '.notxt':
            with open(file, 'w') as f:
                f.write(content)
        
        case '.png':
            with open(file, 'wb') as f:
                f.write(base64.b64decode(content))

        case '.jpg':
            with open(file, 'wb') as f:
                f.write(base64.b64decode(content))

        case '.jpeg':
            with open(file, 'wb') as f:
                f.write(base64.b64decode(content))

        case '.pdf':
            with open(file, 'wb') as f:
                f.write(base64.b64decode(content))

        case _:
            with open(file, 'w') as f:
                f.write(content)

    os.replace(file, f"received_{file}")
    print(f"Vous avez reçu un fichier de la part de {data['sender']} -> {filename}{extension}")

def send_message(username):
    recipient = input("Entrez le destinataire : ")
    sender = username 
    
    print("Entrez votre message (ou 'exit' pour quitter) :")
    while True:
        message = input(f"Pour {recipient}: ")
        if message.lower() == 'exit':
            os.system('cls' if os.name == 'nt' else 'clear')
            break  # Quitter la conversation
        try:
            data = {'type': 'message', 'sender': sender, 'recipient': recipient, 'message': message, 'time': time.strftime("%H:%M:%S")}
            client.send(json.dumps(data).encode())
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'envoi du message: {e}")
            break

def receive_message(client):
    while True:
        try:
            msg = client.recv(10000000).decode()
            if msg:
                # Modification ici pour formatter correctement les messages reçus
                try:
                    msg_data = json.loads(msg)
                    if 'sender' in msg_data and 'message' in msg_data:
                        time = str(msg_data['time'])
                        formatted_msg = f"[{time}] - {msg_data['sender']} : {msg_data['message']}"
                        print(formatted_msg)
                    
                    elif 'sender' in msg_data and 'filename' in msg_data:
                        receive_file(msg_data)
                    else:
                        print(msg)

                except json.JSONDecodeError:
                    print(msg)
            else:
                break  # Si aucun message, cela signifie que le serveur est déconnecté
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")
            break

# Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

# Processus d'authentification
print(" _____         __          __ _             _")
print("|  __ \        \ \        / /| |           | |")
print("| |__) | _   _  \ \  /\  / / | |__    __ _ | |_  ___")
print("|  ___/ | | | |  \ \/  \/ /  | '_ \  / _` || __|/ __| ")
print("| |     | |_| |   \  /\  /   | | | || (_| || |_|\__ \ ")
print("|_|      \__, |    \/  \/    |_| |_| \__,_| \__||___/")
print("          __/ |")
print("         |___/")
print("--------------------------------------------------------")
while True:
    
    action = input("Voulez-vous vous connecter (login) ou créer un compte (register)? ")
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")

    if action in ['login', 'register']:
        data = {'type': action, 'username': username, 'password': password}
        client.send(json.dumps(data).encode())
        response = client.recv(1024).decode()
        print(response)
        if "Connexion réussie" in response or "Compte créé avec succès" in response:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(" ____   _")
            print("|  _ \ (_)")
            print("| |_) | _   ___  _ __  __   __  ___  _ __   _   _   ___")
            print("|  _ < | | / _ \| '_ \ \ \ / / / _ \| '_ \ | | | | / _ \ ")
            print("| |_) || ||  __/| | | | \ V / |  __/| | | || |_| ||  __/")
            print("|____/ |_| \___||_| |_|  \_/   \___||_| |_| \__,_| \___|")
            print("--------------------------------------------------------")
            break

# Lancement du thread de réception des messages après authentification
threading.Thread(target=receive_message, args=(client,)).start()

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
            send_message(username)

        case '2':
            send_file(username)

        case '3':
            data = {'type': 'connected'}
            client.send(json.dumps(data).encode())
            sleep(3)

        case '4':
            newUpdate = update_profile(username)
            if newUpdate != "Null":
                username = newUpdate

        case '5':
            data = {'type': 'logout', 'sender': username}
            client.send(json.dumps(data).encode())
            print("Déconnexion...")
            break

        case _:
            print("Choix invalide. Veuillez réessayer.")

client.close()
