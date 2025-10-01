#!/usr/bin/env python3
"""
server.py
Servidor de controle TCP que envia um arquivo via TCP (mesma conexão) ou UDP (para IP/porta do cliente).
Mede o tempo de transmissão (somente o tempo do envio efetivo do arquivo, no servidor) e retorna ao cliente.
"""

import argparse
import socket
import json
import os
import time

FILE_URL = "https://file-examples.com/storage/fe90bd970b68dc58f98d738/2017/04/file_example_MP4_1920_18MG.mp4"
DEFAULT_FILENAME = "file_example_MP4_1920_18MG.mp4"

def check_file_exists(filename):
    if os.path.exists(filename):
        print(f"Arquivo encontrado localmente: {filename} ({os.path.getsize(filename)} bytes)")
        return

def send_json(sock, obj):
    data = json.dumps(obj).encode('utf-8') + b'\n'
    sock.sendall(data)

def recv_json(sock_file):
    line = sock_file.readline()
    if not line:
        return None
    return json.loads(line.decode('utf-8').strip())

def send_TCP(conn, addr, filename, bufsize):
    # Envia via a mesma conexão TCP
    # O cliente sabe o tamanho e ficará lendo até atingir filesize
    with open(filename, 'rb') as f:
        print("[*] Iniciando envio TCP...")
        start = time.perf_counter()
        bytes_sent = 0
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            conn.sendall(chunk)
            bytes_sent += len(chunk)
        end = time.perf_counter()
        elapsed = end - start
        print(f"Envio TCP finalizado. Bytes enviados: {bytes_sent}. Tempo: {elapsed:.6f}s")
        # Envia resultado ao cliente (via conexão de controle ainda aberta)
        # Para não misturar com o fluxo de dados, enviamos um JSON (o cliente vai ler após receber todos os bytes)
        send_json(conn, {"result": {"protocol": "TCP", "bytes_sent": bytes_sent, "elapsed_s": elapsed}})

def send_UDP(conn, addr, filename, bufsize, req):
    client_udp_port = req.get('udp_port')
    if client_udp_port is None:
        send_json(conn, {"error": "O cliente não forneceu o UDP"})
        return

    client_ip = addr[0]
    print(f"[*] Preparando envio UDP para {client_ip}:{client_udp_port}")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(filename, 'rb') as f:
        start = time.perf_counter()
        bytes_sent = 0
        seq = 0

        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break

            udp_sock.sendto(chunk, (client_ip, client_udp_port))
            bytes_sent += len(chunk)
            seq += 1

        end = time.perf_counter()
        elapsed = end - start

        print(f"Envio UDP finalizado. Pacotes enviados: {seq}. Bytes: {bytes_sent}. Tempo: {elapsed:.6f}s")
        # Fecha socket UDP
        udp_sock.close()
        # Envia resultado ao cliente via controle TCP
        send_json(conn, {"result": {"protocol": "UDP", "bytes_sent": bytes_sent, "elapsed_s": elapsed, "packets": seq}})

def handle_client(conn, addr, filename, bufsize):
    print(f"[+] Conexão de controle aceita: {addr}")
    sock_file = conn.makefile('rb')
    try:
        # Recebe pedido inicial do cliente
        req = recv_json(sock_file)
        if not req:
            print("[-] cliente desconectou antes de enviar dados.")
            return
        
        mode = req.get('mode')  # "TCP" ou "UDP"
        print(f"Modo solicitado pelo cliente: {mode}")

        filesize = os.path.getsize(filename)
        # Envia metadados iniciais para o cliente
        send_json(conn, {"status": "ready", "filename": os.path.basename(filename), "filesize": filesize, "bufsize": bufsize})

        if mode == "TCP":
            send_TCP(conn, addr, filename, bufsize)
            
        elif mode == "UDP":
            send_UDP(conn, addr, filename, bufsize, req)
        else:
            send_json(conn, {"error": "modo desconhecido"})
    except Exception as e:
        print("Erro durante o atendimento ao cliente:", e)
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        conn.close()
        print(f"[-] Conexão de controle encerrada: {addr}")

def start_server(host, port, filename, bufsize):
    check_file_exists(filename)

    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind((host, port))
    serv.listen(5)

    print(f"Servidor de controle escutando em {host}:{port}. Arquivo a servir: {filename}")

    try:
            conn, addr = serv.accept()
            handle_client(conn, addr, filename, bufsize)
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo usuário.")
    finally:
        serv.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor para transferência de arquivo (TCP/UDP).")
    parser.add_argument('--host', default='0.0.0.0', help='Host para bind (default 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Porta de controle TCP (default 9000)')
    parser.add_argument('--file', default=DEFAULT_FILENAME, help='Nome do arquivo local')
    parser.add_argument('--bufsize', type=int, default=65536, help='Tamanho do buffer em bytes (default 65536)')
    args = parser.parse_args()
    start_server(args.host, args.port, args.file, args.bufsize)
