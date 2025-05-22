import socket
import os
import threading
import time

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

clear_flag = threading.Event()

def clear_screen_periodically():
    while True:
        time.sleep(60)
        clear_flag.set()

def main():
    last_five = []
    threading.Thread(target=clear_screen_periodically, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        patient_name = sock.recv(1024).decode('utf-8').strip()

        while True:
            # Only clear after a response, never while typing
            if clear_flag.is_set():
                os.system('cls' if os.name == 'nt' else 'clear')
                clear_flag.clear()

            query = input(f"\nEnter your question for {patient_name}: ").strip()
            if query.lower() == 'exit':
                break

            last_five.append(query)
            if len(last_five) > 5:
                last_five = last_five[-5:]

            sock.sendall(query.encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            print("\nResponse from patient:")
            print(response)

if __name__ == '__main__':
    main()
