import socket
import os
import threading
import time

SERVER_IP = '192.168.1.100'  # Change to your server's IP if needed
SERVER_PORT = 65432

clear_flag = threading.Event()

def clear_screen_periodically():
    while True:
        time.sleep(60)
        clear_flag.set()

def receive_full_response(sock):
    buffer = ""
    while True:
        chunk = sock.recv(64).decode('utf-8')
        buffer += chunk
        if "<<END_OF_RESPONSE>>" in buffer:
            response = buffer.replace("<<END_OF_RESPONSE>>", "")
            return response

def main():
    last_five = []
    threading.Thread(target=clear_screen_periodically, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        patient_name = sock.recv(1024).decode('utf-8').strip()

        while True:
            if clear_flag.is_set():
                os.system('cls' if os.name == 'nt' else 'clear')
                clear_flag.clear()

            query = input(f"\nDoctor: ").strip()
            if query.lower() == 'exit':
                break

            last_five.append(query)
            if len(last_five) > 5:
                last_five = last_five[-5:]

            sock.sendall(query.encode('utf-8'))
            response = receive_full_response(sock)
            print(f"\n{patient_name}: {response}")

if __name__ == '__main__':
    main()
