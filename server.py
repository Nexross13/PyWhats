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
        return "Connexion réussie"
    else:
        return "Échec de connexion"
    
def register(username, password):
    print(users)
    if username in users:
        return False
    else:
        users[username] = password
        save_users(users)
        return True

def update_profile(data):
    if data['code'] == 'username':
        old_username = data['old_username']
        new_username = data['new_username']
        users[new_username] = users.pop(old_username)
        clients[new_username] = clients.pop(old_username)
        save_users(users)

def handle_client(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            data = json.loads(msg)

            match data['type']:
                case 'login':
                    username, password = data['username'], data['password']
                    if login(username, password):
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

        except:
            # Gérer la déconnexion d'un client
            client.close()
            break

def accept_connections():
    while True:
        client, client_address = server.accept()
        print(f"{client_address} s'est connecté.")
        addresses[client] = client_address
        threading.Thread(target=handle_client, args=(client,)).start()

print("Le serveur est démarré...")
accept_connections()