import socket
import time

address = ('localhost', 20000)
name = ""


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(address)

while not name:
    print("Digite seu nome: ")
    name = input()
    if name:
        client_socket.send(name.encode())
        print(client_socket.recv(4096).decode())


while True:
    your_turn = client_socket.recv(4096)
    time.sleep(0.5)
    if your_turn == b"true":
        print(client_socket.recv(4096).decode())              
        print(client_socket.recv(4096).decode(), end="\n")    
        print(client_socket.recv(4096).decode())              
        print("Digite uma letra ou tente adivinhar a palavra\nDigite sair para desconectar\n> ", end="")
        answer = input()
        client_socket.send(bytes(answer, "utf-8"))  
    elif your_turn == b"win":
        print("\nO jogo acabou, você venceu!")
        client_socket.close()
        break
    elif your_turn == b"end":
        print(client_socket.recv(4096).decode())    
        print(client_socket.recv(4096).decode())    
        print(client_socket.recv(4096).decode())   
        print("O jogo acabou, você perdeu")
        client_socket.close()
        break
    else:
        print(client_socket.recv(4096).decode())
        print("Espere sua vez\n")
