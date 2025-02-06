import socket
import os
import json
import re

HOST = '192.168.3.2'
PORT_UDP = 5005
PORT_TCP = 5009
BUFFER_SIZE = 12000
FTP_DIRECTORY = "ftp/"

FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\. ]+$')

def validar_nome_arquivo(nome_arquivo):
    if not FILENAME_PATTERN.match(nome_arquivo) or ".." in nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
        return False
    return True

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((HOST, PORT_UDP))

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, PORT_TCP))
tcp_socket.listen(1)

def listar_arquivos():
    return {"status": "success", "data": os.listdir(FTP_DIRECTORY)}

def excluir_arquivo(nome_arquivo):
    try:
        os.remove(os.path.join(FTP_DIRECTORY, nome_arquivo))
        return {"status": "success", "data": f"arquivo '{nome_arquivo}' excluído!"}
    except Exception as e:
        return {"status": "error", "message": f"erro ao excluir o arquivo '{nome_arquivo}': {str(e)}"}

def receber_arquivo(nome_arquivo):
    conexao_tcp, _ = tcp_socket.accept()
    with open(os.path.join(FTP_DIRECTORY, nome_arquivo), 'wb') as f:
        while data := conexao_tcp.recv(1024):
            f.write(data)
    conexao_tcp.close()
    return {"status": "success", "message": f"arquivo '{nome_arquivo}' recebido!"}

def enviar_arquivo(nome_arquivo):
    conexao_tcp, _ = tcp_socket.accept()
    caminho_arquivo = os.path.join(FTP_DIRECTORY, nome_arquivo)
    try:
        with open(caminho_arquivo, 'rb') as f:
            while chunk := f.read(1024):
                conexao_tcp.send(chunk)
        resposta = {"status": "success", "message": f"arquivo '{nome_arquivo}' enviado com sucesso"}
    except FileNotFoundError:
        resposta = {"status": "error", "message": "arquivo não encontrado"}
    conexao_tcp.close()
    return resposta

try:
    while True:
        msg, cliente = udp_socket.recvfrom(BUFFER_SIZE)
        args = msg.decode('utf-8').split()

        resposta = {"status": "error", "message": "comando inválido"}
        
        if len(args) == 0:
            resposta = {"status": "error", "message": "comando vazio"}
        elif args[0] == "listar":
            resposta = listar_arquivos()
        elif len(args) == 2:
            if not validar_nome_arquivo(args[1]):
                resposta =  {"status": "error", "message": "nome de arquivo inválido"}
            else:
                if args[0] == "excluir":
                    resposta = excluir_arquivo(args[1])
                elif args[0] == "enviar":
                    resposta = receber_arquivo(args[1])
                elif args[0] == "download":
                    resposta = enviar_arquivo(args[1])
            
        udp_socket.sendto(json.dumps(resposta).encode('utf-8'), cliente)
finally:
    udp_socket.close()
    tcp_socket.close()