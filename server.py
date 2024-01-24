import socket
import threading
import json
import os

# Configuration initiale du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 12345))
server.listen()

clients = {}
addresses = {}

# Fonction pour charger les utilisateurs depuis users.json
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    else:
        return {}

# Fonction pour sauvegarder les utilisateurs dans users.json
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)

users = load_users()

def whoIsConnected(clients):
    connected_users = list(clients.keys())
    formatted_list = "Utilisateurs connectés:\n" + "\n".join(f"   - {user}" for user in connected_users)
    return formatted_list

def login(username, password):
    if username in users and users[username] == password:
        return True
    else:
        return False
    
def register(username, password):
    if username in users:
        return False
    else:
        users[username] = password
        save_users(users)
        return True

def update_profile(data):
    if data['code'] == 'username' and data['new_username'] not in users:
        old_username = data['sender']
        new_username = data['new_username']
        users[new_username] = users.pop(old_username)
        clients[new_username] = clients.pop(old_username)
        save_users(users)

    elif data['code'] == 'password':
        username = data['sender']
        new_password = data['password']
        users[username] = new_password
        save_users(users)
    
    else:
        print("Nom d'utilisateur déjà pris")

def file_transfer(data):
    # Première étape: le serveur reçoit les données du fichier
    print("Fichier en cours de récéption...")
    print("Fichier reçu")
    # Deuxième étape: le serveur envoie les données du fichier au destinataire
    print("Fichier en cours d'envoi...")
    clients[data['recipient']].send(json.dumps(data).encode())
    print("Fichier envoyé")


def handle_client(client):
    while True:
        try:
            msg = client.recv(100000000).decode()
            data = json.loads(msg)

            match data['type']:
                case 'login':
                    username, password = data['username'], data['password']
                    if login(username, password) and username not in clients:
                        client.send("Connexion réussie".encode())
                        clients[username] = client
                    else:
                        client.send("Échec de connexion".encode())
                
                case 'register':
                    username, password = data['username'], data['password']
                    if not register(username, password):
                        client.send("Nom d'utilisateur déjà pris".encode())
                    else:
                        client.send("Compte créé avec succès".encode())
                        clients[username] = client

                case 'connected':
                    client.send(whoIsConnected(clients).encode())
                
                case 'message':
                    recipient = data['recipient']
                    if recipient in clients:
                        clients[recipient].send(json.dumps(data).encode())
                    else:
                        client.send("Destinataire non connecté".encode())
                
                case 'update':
                    update_profile(data)

                case 'file':
                    if data['recipient'] in clients:
                        file_transfer(data)
                    else:
                        client.send("Destinataire non connecté".encode())
                    
                case 'logout':
                    username = data['sender']
                    client.close()
                    del addresses[client]
                    del clients[username]
                    print(f"{username} s'est déconnecté.")
                    break

        except:
            # Gérer la déconnexion d'un client
            break

def accept_connections():
    while True:
        client, client_address = server.accept()
        print(f"{client_address} s'est connecté.")
        addresses[client] = client_address
        threading.Thread(target=handle_client, args=(client,)).start()

print("Le serveur est démarré...")
accept_connections()