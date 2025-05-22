import socket
import os
import threading
import time

# Paste your full patients list here, or just the names as below:
patients = [
    [1, "Julian", ""],
    [2, "Emily", ""],
    [3, "Sophia", ""],
    [4, "Camila", ""],
    [5, "Connor", ""],
    [6, "Ben", ""],
    [7, "Aidan", ""],
    [8, "Emma", ""],
    [9, "Lizzy", ""],
    [10, "Michaela", ""],
    [11, "Ian", ""],
    [12, "Samira", ""],
    [13, "Ethan", ""],
    [14, "Jackson", ""],
    [15, "Grace", ""],
    [16, "Olivia", ""]
]

SERVER_IP = '192.168.1.100'   # Change to your server's IP if needed
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

    print("Available scenarios:")
    for patient in patients:
        print(f"{patient[0]}. {patient[1]}")

    while True:
        try:
            scenario = int(input("Choose scenario (1-16): "))
            if 1 <= scenario <= 16:
                break
            print("Invalid choice. Try again.")
        except ValueError:
            print("Numbers only please.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        # Send scenario number as first message
        sock.sendall(str(scenario).encode('utf-8'))
        # Receive patient name from server
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
