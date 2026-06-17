import socket
import os
import json

HOST = '0.0.0.0'
PORT = 65432
FOLDER = 'files'

if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def xor_encrypt_decrypt(data, key=b'mykey'):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def validate_json(content):
    try:
        json.loads(content)
        return True
    except:
        return False

def validate_xml(content):
    return content.strip().startswith('<') and content.strip().endswith('>')

def handle_client(conn):
    while True:
        command = conn.recv(1024).decode()
        if not command:
            break
        if command == 'UPLOAD':
            filename = conn.recv(1024).decode()
            extension = filename.split('.')[-1]
            if extension not in ('json', 'xml'):
                conn.send(b'ERROR: Unsupported format')
                continue
            size_bytes = conn.recv(8)
            filesize = int.from_bytes(size_bytes, 'big')
            data = b''
            while len(data) < filesize:
                data += conn.recv(4096)
            if extension == 'json':
                valid = validate_json(data.decode())
            else:
                valid = validate_xml(data.decode())
            if not valid:
                conn.send(b'ERROR: Validation failed')
                continue
            encrypted = xor_encrypt_decrypt(data)
            filepath = os.path.join(FOLDER, filename + '.bin')
            with open(filepath, 'wb') as f:
                f.write(encrypted)
            conn.send(b'SUCCESS')
        elif command == 'DOWNLOAD':
            filename = conn.recv(1024).decode()
            filepath = os.path.join(FOLDER, filename + '.bin')
            if not os.path.exists(filepath):
                conn.send(b'ERROR: File not found')
                continue
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            size_bytes = len(encrypted_data).to_bytes(8, 'big')
            conn.send(size_bytes)
            conn.sendall(encrypted_data)
        elif command == 'EXIT':
            break
        else:
            conn.send(b'ERROR: Unknown command')
    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        handle_client(conn)