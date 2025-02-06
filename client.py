import socket 
import os
import json
import time

HOST = '192.168.3.2'
PORT_UDP = 5005
PORT_TCP = 5009
BUFFER_SIZE = 12000

def enviar_arquivo_tcp(socket_tcp, caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        while chunk := f.read(1024):
            socket_tcp.send(chunk)

def receber_arquivo_tcp(socket_tcp, nome_arquivo):
    with open(nome_arquivo, 'wb') as f:
        while data := socket_tcp.recv(1024):
            f.write(data)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Conectado a:", (HOST, PORT_UDP))
print("Para sair, pressione 'CTRL + X'")
msg = input()

try:
    while msg != '\x18':
        args = msg.split()
        if args[0] == "enviar" and len(args) == 2:
            caminho_arquivo = args[1]
            if os.path.exists(caminho_arquivo):
                udp_socket.sendto(msg.encode("utf-8"), (HOST, PORT_UDP))
                time.sleep(1)
                
                # Criar socket TCP antes de conectar
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.connect((HOST, PORT_TCP))
                enviar_arquivo_tcp(tcp_socket, caminho_arquivo)
                tcp_socket.close()
                time.sleep(1)
            else:
                print("Arquivo não existe.")
        elif args[0] == "download" and len(args) == 2:
            udp_socket.sendto(msg.encode("utf-8"), (HOST, PORT_UDP))
            time.sleep(1)

            # Criar novo socket TCP antes de conectar
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((HOST, PORT_TCP))
            receber_arquivo_tcp(tcp_socket, args[1])
            tcp_socket.close()
        else:
            udp_socket.sendto(msg.encode("utf-8"), (HOST, PORT_UDP))

        data, _ = udp_socket.recvfrom(BUFFER_SIZE)
        print(json.loads(data.decode('utf-8')))
        msg = input()
finally:
    udp_socket.close()
