import socket
import json
import threading

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
    print("3. Se déconnecter")
    choix = input("Que souhaitez-vous faire? (Entrez le numéro de l'option) : ")

    if choix == '1':
        recipient = input("Entrez le destinataire : ")
        sender = username 
        
        while True:
            message = input("Entrez votre message (ou 'exit' pour quitter) : ")
            if message.lower() == 'exit':
                break  # Quitter la conversation
            try:
                data = {'type': 'message', 'sender': sender, 'recipient': recipient, 'message': message}
                client.send(json.dumps(data).encode())
            except Exception as e:
                print(f"Une erreur s'est produite lors de l'envoi du message: {e}")
                break

    elif choix == '2':
        data = {'type': 'connected'}
        client.send(json.dumps(data).encode())


    elif choix == '3':
        print("Déconnexion...")
        break
    else:
        print("Choix invalide. Veuillez réessayer.")

client.close()
