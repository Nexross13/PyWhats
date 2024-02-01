import json
import select
import socket
import threading

clients = {}

def Debug(message):
    print("[DEBUG] : ", message)

def ConnexionOpen():
    print("   _____                             ____                   ")
    print("  / ____|                           / __ \                  ")
    print(" | (___   ___ _ ____   _____ _ __  | |  | |_ __   ___ _ __  ")
    print("  \___ \ / _ \ '__\ \ / / _ \ '__| | |  | | '_ \ / _ \ '_ \ ")
    print("  ____) |  __/ |   \ V /  __/ |    | |__| | |_) |  __/ | | |")
    print(" |_____/ \___|_|    \_/ \___|_|     \____/| .__/ \___|_| |_|")
    print("                                          | |               ")
    print("----------------------------------------- |_| --------------")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 12345))
    server.listen()
    return server

def Login(client, username, password):
    Debug("Begin login...")
    with open("users.json", "r") as file:
        users = json.load(file)
        file.close()
    
    Debug("Begin search...")
    if username in users and users[username] == password:
        clients[username] = client
        Debug(f"User {username} has been successfully logged in")
        return True
    else:
        Debug("User not found")
        return False

def Register(client, username, password):
    isEmpty = False
    users = {}
    Debug("Current record...")
    with open("users.json", "r") as file:
        file_content = file.read()
        if file_content == '':
            Debug("File is empty")
            isEmpty = True
        else:
            Debug("File is not empty")
            users = json.loads(file_content)
        file.close()
    
    if isEmpty == False:
        Debug("Begin search...")
        if username in users:
            Debug("User already exists")
            return False
        else:
            Debug("User not found, adding...")
            users[username] = password
            Debug("Writing to file...")
            with open("users.json", "w") as file:
                json.dump(users, file)
                file.close()
            Debug("Adding client to dictionnary...")
            clients[username] = client
            Debug(f"User {username} hase been successfully added to database")
            return True
    else:
        Debug("File is empty, adding first user...")
        users[username] = password
        with open("users.json", "w") as file:
            json.dump(users, file)
            file.close()
        clients[username] = client
        Debug(f"User {username} has been successfully added to database")
        return True

def UpdateUsername(old_username, new_username):
    with open("users.json", "r") as file:
        users = json.load(file)
        file.close()
    
    for user in users:
        if user['username'] == new_username:
            return False
        else:
            user['username'] = new_username
            with open("users.json", "w") as file:
                json.dump(users, file)
                file.close()
            clients[new_username] = clients.pop(old_username)
            return True
        
def UpdatePassword(username, password):
    with open("users.json", "r") as file:
        users = json.load(file)
        file.close()
    
    for user in users:
        if user['username'] == username:
            user['password'] = password
            with open("users.json", "w") as file:
                json.dump(users, file)
                file.close()
            return True
        else:
            return False
    
def SendToClient(client, sender, recipient, message):
    if recipient in clients :
        Debug("Client found, preparing message...")
        data = {'type': 'message', 'sender': sender, 'message': message}
        try: 
            clients[recipient].send(json.dumps(data).encode())
            Debug(f"Message sent to {recipient}")
        except Exception as e:
            Debug("Error while sending message : ", e)

def SendFile(client, sender, recipient, filename, extension, file):
    for client in clients:
        if clients[client] == recipient:
            data = {'type': 'file', 'sender': sender, 'filename': filename, 'extension': extension, 'file': file}
            client.send(json.dump(data).encode())

def HandleClient(client):
    while True:
        try:
            data = client.recv(100000).decode()
            data = json.loads(data)
            type = data['type']
            match type:
                case "login":
                    Debug("Received login request")
                    username = data['username']
                    password = data['password']
                    if Login(client, username, password):
                        client.send("OK".encode())
                    else:
                        client.send("KO".encode())

                case "register":
                    print("Received register request")
                    print(data)
                    username = data['username']
                    password = data['password']
                    if Register(client, username, password):
                        client.send("OK".encode())
                    else:
                        client.send("KO".encode())

                case "message":
                    Debug("Received message request")
                    sender = data['sender']
                    recipient = data['recipient']
                    message = data['message']
                    Debug(f"Sending message to {recipient}...")
                    SendToClient(client, sender, recipient, message)

                case "update_username":
                    old_username = data['username']
                    new_username = data['newUsername']
                    if UpdateUsername(old_username, new_username):
                        client.send("OK".encode())
                    else:
                        client.send("KO".encode())

                case "update_password":
                    username = data['username']
                    password = data['newPassword']
                    if UpdatePassword(username, password):
                        client.send("OK".encode())
                    else:
                        client.send("KO".encode())

                case "file":
                    sender = data['sender']
                    recipient = data['recipient']
                    filename = data['filename']
                    extension = data['extension']
                    file = data['file']
                    SendFile(client, sender, recipient, filename, extension, file)

                case "is_connected":
                    username = data['recipient']
                    Debug(f"Checking if {username} is connected...")
                    if username in clients:
                        Debug(f"{username} is connected")
                        client.send("OK".encode())
                        
                    else:
                        Debug(f"{username} is not connected")
                        client.send("KO".encode())
                    
                    Debug("End of check")

                case _:
                    print("Type de message inconnu")

        except Exception as e:
            print(e)
            break

def Main():
    server = ConnexionOpen()
    while True:
        client, address = server.accept()
        print("Connexion de " + str(client))
        threading.Thread(target=HandleClient, args=(client, )).start()

if __name__ == "__main__":
    Main()