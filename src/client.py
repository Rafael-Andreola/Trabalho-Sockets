#!/usr/bin/env python3
"""
client.py
Cliente que se conecta ao servidor de controle (TCP), escolhe TCP ou UDP, recebe o arquivo e mostra o tempo de transmissão retornado pelo servidor.
"""

import argparse
import socket
import json
import os

def send_json(sock, obj):
    data = json.dumps(obj).encode('utf-8') + b'\n'
    sock.sendall(data)

def recv_json(sock_file):
    line = sock_file.readline()
    if not line:
        return None
    return json.loads(line.decode('utf-8').strip())

def receive_tcp_file(control_conn, sock_file, out_filename, expected_size):
    with open(out_filename, 'wb') as f:
        remaining = expected_size
        while remaining > 0:
            chunk = control_conn.recv(min(1, remaining))
            if not chunk:
                raise IOError("Conexão encerrada antes de receber todos os bytes")
            f.write(chunk)
            remaining -= len(chunk)

def receive_udp_file(udp_sock, out_filename, expected_size, timeout=10.0):
    udp_sock.settimeout(timeout)
    received = 0
    with open(out_filename, 'wb') as f:
        try:
            while received < expected_size:
                data, addr = udp_sock.recvfrom(65536 + 64)
                if not data:
                    break
                f.write(data)
                received += len(data)
        except socket.timeout:
            print("Timeout UDP: não foram recebidos todos os bytes antes do timeout.")
    return received

def main(server_ip, port, bufsize):
    print("=== Cliente de transferência de arquivo ===")
    print("Escolha protocolo:")
    print("1) TCP")
    print("2) UDP")
    choice = input("Opção [1/2]: ").strip()
    if choice == '1':
        mode = "TCP"
    else:
        mode = "UDP"

    ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl.connect((server_ip, port))
    sock_file = ctrl.makefile('rb')

    if mode == "TCP":
        # Envia pedido inicial ao servidor
        send_json(ctrl, {"mode": "TCP"})
        # Recebe "ready" com metadados
        meta = recv_json(sock_file)
        if not meta or meta.get('status') != 'ready':
            print("[-] Servidor não pronto ou erro:", meta)
            ctrl.close()
            return
        filename = meta['filename']
        filesize = meta['filesize']
        print(f"Servidor pronto. Arquivo: {filename} ({filesize} bytes). Iniciando recebimento por TCP...")
        out_name = f"received_tcp_{filename}"
        receive_tcp_file(ctrl, ctrl, out_name, filesize)
        print(f"Recebido arquivo em {out_name}. Aguardando resultado do servidor...")
        
        result = recv_json(sock_file)
        if result and 'result' in result:
            r = result['result']
            print(f"[RESULTADO] protocolo={r.get('protocol')}, bytes_sent={r.get('bytes_sent')}, tempo_s={r.get('elapsed_s'):.6f}")
        else:
            print("Resultado não recebido ou formato inesperado:", result)
        ctrl.close()
    else:
        # UDP mode: precisa abrir socket UDP e informar porta ao servidor
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('', 0))  # porta aleatória disponível
        udp_port = udp_sock.getsockname()[1]
        print(f"Porta UDP local escolhida: {udp_port}")
        send_json(ctrl, {"mode": "UDP", "udp_port": udp_port})
        meta = recv_json(sock_file)

        if not meta or meta.get('status') != 'ready':
            print("- Servidor não pronto ou erro:", meta)
            ctrl.close()
            return
        
        filename = meta['filename']
        filesize = meta['filesize']
        print(f"Servidor pronto. Arquivo: {filename} ({filesize} bytes). Iniciando recebimento por UDP...")

        out_name = f"received_udp_{filename}"
        received = receive_udp_file(udp_sock, out_name, filesize, timeout=20.0)
        print(f"Recebidos {received} bytes (esperados {filesize}). Aguardando resultado do servidor via TCP...")
        result = recv_json(sock_file)
        if result and 'result' in result:
            r = result['result']
            print(f"[RESULTADO] protocolo={r.get('protocol')}, bytes_sent={r.get('bytes_sent')}, tempo_s={r.get('elapsed_s'):.6f}, pacotes={r.get('packets')}")
        else:
            print("Resultado não recebido ou formato inesperado:", result)
        udp_sock.close()
        ctrl.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente para teste de transferência TCP/UDP.")
    parser.add_argument('--server', required=True, help='IP do servidor')
    parser.add_argument('--port', type=int, default=9000, help='Porta de controle TCP do servidor (default 9000)')
    parser.add_argument('--bufsize', type=int, default=65536, help='Tamanho do buffer usado no lado cliente (apenas informativo)')
    args = parser.parse_args()
    main(args.server, args.port, args.bufsize)
