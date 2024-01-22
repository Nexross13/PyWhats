import socket
import json
import threading

def update_profile(username):
    print("\nMenu :")
    print("1. Modifier le nom d'utilisateur")
    print("2. Modifier le mot de passe")
    print("3. exit")
    choix = input("Que souhaitez-vous faire? (Entrez le numéro de l'option) : ")
    match choix :
        case '1':
            new_username = input("Entrez le nouveau nom d'utilisateur : ")
            data = {'type': 'update', 'code': 'username', 'old_username': username, 'new_username': new_username}
            client.send(json.dumps(data).encode())
        
        case '2':
            new_password = input("Entrez le nouveau mot de passe : ")
            data = {'type': 'update', 'code': 'password', 'password': new_password}
            client.send(json.dumps(data).encode())
        
        case '3':
            print('')

        case _:
            print("Choix invalide. Veuillez réessayer.")    

def receive_message(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                # Modification ici pour formatter correctement les messages reçus
                try:
                    msg_data = json.loads(msg)
                    if 'sender' in msg_data and 'message' in msg_data:
                        formatted_msg = f"[{msg_data['sender']}] : {msg_data['message']}"
                        print(formatted_msg)
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
            break

# Lancement du thread de réception des messages après authentification
threading.Thread(target=receive_message, args=(client,)).start()

# Menu après authentification
while True:
    print("\nMenu :")
    print("1. Envoyer un message")
    print("2. Voir qui est connecté")
    print("3. Modifier son profil")
    print("4. Se déconnecter")
    choix = input("Que souhaitez-vous faire? (Entrez le numéro de l'option) : ")

    match choix :
        case '1':
            recipient = input("Entrez le destinataire : ")
            sender = username 
            
            print("Entrez votre message (ou 'exit' pour quitter) :")
            while True:
                message = input("Pour ", recipient, ": ")
                if message.lower() == 'exit':
                    break  # Quitter la conversation
                try:
                    data = {'type': 'message', 'sender': sender, 'recipient': recipient, 'message': message}
                    client.send(json.dumps(data).encode())
                except Exception as e:
                    print(f"Une erreur s'est produite lors de l'envoi du message: {e}")
                    break

        case '2':
            data = {'type': 'connected'}
            client.send(json.dumps(data).encode())

        case '3':
            update_profile(username)

        case '4':
            print("Déconnexion...")
            break
        case _:
            print("Choix invalide. Veuillez réessayer.")

client.close()
