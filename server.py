import socket
import threading
import json
import os

# Configuration initiale du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    if username in users:
        return "Nom d'utilisateur déjà pris"
    else:
        users[username] = password
        save_users(users)
        return "Compte créé avec succès"

def handle_client(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            data = json.loads(msg)

            if data['type'] == 'login':
                username, password = data['username'], data['password']
                if login(username, password):
                    client.send("Connexion réussie".encode())
                    clients[username] = client
                else:
                    client.send("Échec de connexion".encode())

            elif data['type'] == 'register':
                username, password = data['username'], data['password']
                if register(username, password):
                    client.send("Nom d'utilisateur déjà pris".encode())
                else:
                    client.send("Compte créé avec succès".encode())
                    clients[username] = client
                    # Envoi de la liste des utilisateurs connectés

            elif data['type'] == 'connected':
                client.send(whoIsConnected(clients).encode())
                    
            elif data['type'] == 'message':
                recipient = data['recipient']
                if recipient in clients:
                    clients[recipient].send(json.dumps(data).encode())
                else:
                    client.send("Destinataire non connecté".encode())

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