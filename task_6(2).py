import socket
import os

HOST = '127.0.0.1'
PORT = 65432

def send_file(sock, filepath):
    filename = os.path.basename(filepath)
    extension = filename.split('.')[-1]
    if extension not in ('json', 'xml'):
        print('Поддерживаются только файлы .json и .xml')
        return
    with open(filepath, 'rb') as f:
        data = f.read()
    sock.send(b'UPLOAD')
    sock.send(filename.encode())
    sock.send(len(data).to_bytes(8, 'big'))
    sock.sendall(data)
    response = sock.recv(1024)
    print('Ответ сервера:', response.decode())

def download_file(sock, filename):
    sock.send(b'DOWNLOAD')
    sock.send(filename.encode())
    size_bytes = sock.recv(8)
    filesize = int.from_bytes(size_bytes, 'big')
    received = 0
    encrypted_data = b''
    while received < filesize:
        chunk = sock.recv(4096)
        if not chunk:
            break
        encrypted_data += chunk
        received += len(chunk)
    if encrypted_data.startswith(b'ERROR'):
        print(encrypted_data.decode())
    else:
        with open(f'downloaded_{filename}.bin', 'wb') as f:
            f.write(encrypted_data)
        print(f'Файл {filename} скачан и сохранен как downloaded_{filename}.bin')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    filepath = 'example.json'
    send_file(sock, filepath)
    filename_to_download = 'example.json'
    download_file(sock, filename_to_download)
    sock.send(b'EXIT')