import socket
import sys
import _thread
import time
import random
from view import *

host = "localhost"
port = 20000


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket criada")


try:
    server_socket.bind((host, port))
except socket.error:
    print("Falha na vinculação de endereço", (host, port))
    sys.exit()

print("Socket vinculada ao endereço", (host, port))
server_socket.listen(4)

players = []   
prints = [zero(), one(), two(), three(), four(), five(), six()] 
pool = ["casaco","escola","bicicleta","antigo","lapiseira","vestido","computador","servidor","cliente","cadeira","cachorro","constitucional"] 
errors = 0
hangman = True


def game(chosen_word):
    global players
    global hangman
    global errors

    right_answers = []
    errors = 0
    hangman = True
    copy = chosen_word
    data = ""
    previous = ""

    while True:
        if len(players) >= 2:
            break

    while hangman:
        for p in players:
            p[0].sendto(b"true", p[1])
            print("\nAgora é o turno do jogador: ", p[2])

            time.sleep(0.25)
            p[0].sendto(prints[errors], p[1]) 

            time.sleep(0.25)
            p[0].sendto(underline(chosen_word, right_answers), p[1])  

            if not data:
                time.sleep(0.25)
                p[0].sendto("\nVocê começa!\n".encode(), p[1])
            elif data == "sair":
                time.sleep(0.25)
                p[0].sendto(("\nO jogador " + previous + " saiu\n").encode(), p[1])
            else:
                time.sleep(0.25)
                p[0].sendto(("\nO jogador " + previous + " chutou " + data + "\n").encode(), p[1])

            previous = p[2]

            time.sleep(0.25)
            data = p[0].recv(4096).decode()
            print("Resposta recebida de ", p[2], ": ", data)

            if data == "sair":
                time.sleep(0.3)
                p[0].sendto(b"end", p[1])
                p[0].close()
                players.remove(p)
                break
            elif data == chosen_word:
                right_answers = chosen_word
                print(p[2], " acertou a palavra")
                time.sleep(4.3)
                p[0].sendto(b"win", p[1])
                p[0].close()
                players.remove(p)
                game_over(chosen_word, right_answers, True, p[2])
                break
            elif len(data) == 1 and data in copy:
                copy = copy.replace(data, "")
                if data not in right_answers:
                    right_answers += data
                if not copy:
                    print("\nNinguém acertou a palavra: ", chosen_word, end="\n")
                    game_over(chosen_word, right_answers, False, p[2])
                    break
                print(p[2], " acertou uma: ", data)
            else:
                errors += 1
                if errors >= 6:
                    game_over(chosen_word, right_answers, False, p[2])
                    break
                print(p[2], " errou uma: ", data)

    players = []
    print("Fim de jogo, iniciando outro")
    _thread.start_new_thread(game, (random.choice(pool),))

def game_over(word, answers, won, winner_name):
    global hangman
    global errors

    for i in players:
        time.sleep(0.25)
        i[0].sendto(b"end", i[1])
        time.sleep(0.25)
        i[0].sendto(prints[errors], i[1])
        time.sleep(0.25)
        i[0].sendto(underline(word, answers), i[1])
        if won:
            time.sleep(2.0)
            i[0].sendto(("O jogador " + winner_name + " venceu!").encode(), i[1])
        else:
            time.sleep(2.0)
            i[0].sendto(b"Nao houve vencedor\n", i[1])
        i[0].close()
    hangman = False


def client_thread(conn, player_address):
    name = []
    try:
        name = conn.recv(4096).decode()
        players.append((conn, player_address, name))
        print("Jogador", player_address, "nomeou-se como " + name)

        if len(players) >= 2:
            conn.sendto(("\nBem vindo ao Jogo da Forca, " + name + "\nA sala está completa, vamos começar o jogo!\n").encode(), player_address)
        else:
            conn.sendto(("\nBem vindo ao Jogo da Forca, " + name +
                         "\nNo momento atual temos " + str(len(players)) + " jogadores na sessão, é necessário 2 jogadores para iniciar\n").encode(),
                        player_address)
    except ConnectionResetError:
        if (conn, player_address, name) in players:
            players.remove((conn, player_address, name))
        print("Jogador se desconectou")

_thread.start_new_thread(game, (random.choice(pool),))

while True:
    if len(players) < 1:
        connection, address = server_socket.accept()
        print("Nova conexão recebida de", address)
        _thread.start_new_thread(client_thread, (connection, address))
