import socket
import os
import threading
import time
from inputimeout import inputimeout, TimeoutOccurred

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

clear_flag = threading.Event()

def clear_screen_periodically():
    while True:
        time.sleep(60)
        clear_flag.set()

def main():
    last_five = []

    # Start the screen-clearing timer thread
    threading.Thread(target=clear_screen_periodically, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        patient_name = sock.recv(1024).decode('utf-8').strip()

        while True:
            # Clear the screen if the flag is set and we're not typing
            if clear_flag.is_set():
                os.system('cls' if os.name == 'nt' else 'clear')
                clear_flag.clear()

            try:
                # Wait for input with a timeout of 1 second, so we can check the clear flag frequently
                query = inputimeout(prompt=f"\nEnter your question for {patient_name}: ", timeout=1).strip()
            except TimeoutOccurred:
                continue  # No input, loop again to check for clear

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
