import socket
import os
import threading
import time

patients = [
    [1, "Julian"],
    [2, "Emily"],
    [3, "Sophia"],
    [4, "Camila"],
    [5, "Connor"],
    [6, "Ben"],
    [7, "Aidan"],
    [8, "Emma"],
    [9, "Lizzy"],
    [10, "Michaela"],
    [11, "Ian"],
    [12, "Samira"],
    [13, "Ethan"],
    [14, "Jackson"],
    [15, "Grace"],
    [16, "Olivia"]
]

SERVER_IP = '192.168.1.100'   # Change to your server's IP if needed
SERVER_PORT = 65432

last_activity = time.time()

def clear_screen_if_inactive():
    global last_activity
    while True:
        time.sleep(1)
        if time.time() - last_activity > 120:
            os.system('cls' if os.name == 'nt' else 'clear')
            last_activity = time.time()  # reset timer after clearing

def receive_full_response(sock):
    buffer = ""
    while True:
        chunk = sock.recv(64).decode('utf-8')
        buffer += chunk
        if "<<END_OF_RESPONSE>>" in buffer:
            response = buffer.replace("<<END_OF_RESPONSE>>", "")
            return response

def main():
    global last_activity
    threading.Thread(target=clear_screen_if_inactive, daemon=True).start()

    print("Available scenarios:")
    for patient in patients:
        print(f"{patient[0]}. {patient[1]}")

    while True:
        try:
            scenario = int(input("Choose scenario (1-16): "))
            if 1 <= scenario <= 16:
                last_activity = time.time()
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen immediately after choice
                break
            print("Invalid choice. Try again.")
        except ValueError:
            print("Numbers only please.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(str(scenario).encode('utf-8'))
        patient_name = sock.recv(1024).decode('utf-8').strip()

        while True:
            query = input(f"\nDoctor: ").strip()
            last_activity = time.time()
            if query.lower() == 'exit':
                break

            sock.sendall(query.encode('utf-8'))
            response = receive_full_response(sock)
            print(f"\n{patient_name}: {response}")
            last_activity = time.time()

if __name__ == '__main__':
    main()
