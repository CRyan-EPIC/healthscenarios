import socket
import os
import threading
import time
import sys
import getpass

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

RECONNECT_DELAY = 3  # seconds between reconnect attempts
SOCKET_TIMEOUT = 30  # seconds to wait for server response before retry

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

def receive_full_response(sock):
    buffer = ""
    while True:
        try:
            chunk = sock.recv(64).decode('utf-8')
        except socket.timeout:
            raise TimeoutError("Timed out waiting for server response.")
        if not chunk:
            raise ConnectionError("Server closed connection.")
        buffer += chunk
        if "<<END_OF_RESPONSE>>" in buffer:
            response = buffer.replace("<<END_OF_RESPONSE>>", "")
            return response

def connect_to_server(scenario):
    while True:
        try:
            print(f"Connecting to server and sending scenario number: {scenario}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.sendall(str(scenario).encode('utf-8'))  # Always send scenario number first
            patient_name = sock.recv(1024).decode('utf-8').strip()
            print(f"Connected. Patient name: {patient_name}")
            return sock, patient_name
        except Exception as e:
            print(f"Connection failed ({e}), retrying in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)

def reconnect_and_resend(scenario, last_query):
    sock, patient_name = connect_to_server(scenario)
    try:
        sock.sendall(last_query.encode('utf-8'))
        response = receive_full_response(sock)
    except Exception as e:
        print(f"[Resend failed after reconnect: {e}]")
        response = "[No response after reconnect]"
    return sock, patient_name, response

def choose_scenario():
    print("Available scenarios:")
    for patient in patients:
        print(f"{patient[0]}. {patient[1]}")
    while True:
        try:
            scenario = int(input("Choose scenario (1-16): "))
            if 1 <= scenario <= 16:
                return scenario
            print("Invalid choice. Try again.")
        except ValueError:
            print("Numbers only please.")

def main():
    password = getpass.getpass("Enter password to use the client: ")
    if password != "cyberlab":
        print("Incorrect password. Exiting.")
        sys.exit(1)

    scenario = choose_scenario()

    # --- Clear the screen after selection ---
    os.system('cls' if os.name == 'nt' else 'clear')

    # --- Print scenario selection only ---
    print(f"Choose scenario (1-16): {scenario}")

    sock, patient_name = connect_to_server(scenario)
    last_query = None

    while True:
        try:
            query = input("\nDoctor: ").strip()
            if query.lower() == 'exit':
                break
            if query.lower() == '.switch':
                sock.close()
                scenario = choose_scenario()
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"Choose scenario (1-16): {scenario}")
                sock, patient_name = connect_to_server(scenario)
                continue
            last_query = query
            try:
                sock.sendall(query.encode('utf-8'))
                response = receive_full_response(sock)
            except (TimeoutError, ConnectionError) as e:
                print(f"\n[Lost connection: {e}] Attempting to reconnect...")
                sock.close()
                sock, patient_name, response = reconnect_and_resend(scenario, last_query)
                print("[Reconnected. Resending your last question.]")
            print(f"\n{patient_name}: {response}")
        except KeyboardInterrupt:
            print("\nExiting.")
            break

    sock.close()

if __name__ == '__main__':
    main()
