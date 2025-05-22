import socket
import os
import threading
import time
import sys
import getpass

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

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

RECONNECT_DELAY = 3  # seconds between reconnect attempts
SOCKET_TIMEOUT = 30  # seconds to wait for server response before retry


last_activity = time.time()
input_lock = threading.Lock()
pending_prompt = threading.Event()
idle_triggered = threading.Event()

def clear_screen_and_prompt(patient_name):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nDoctor: ", end='', flush=True)
    pending_prompt.set()

def clear_screen_if_inactive(patient_name):
    global last_activity
    while True:
        time.sleep(1)
        if time.time() - last_activity > 120:
            with input_lock:
                clear_screen_and_prompt(patient_name)
                last_activity = time.time()

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

def idle_mumble(sock, patient_name):
    global last_activity
    while True:
        time.sleep(1)
        if time.time() - last_activity > 60 and not idle_triggered.is_set():
            idle_triggered.set()
            with input_lock:
                try:
                    sock.sendall("...".encode('utf-8'))
                    response = receive_full_response(sock)
                    print(f"\n{patient_name}: {response}")
                except Exception as e:
                    print(f"\n[Idle mumble failed: {e}]")
                print("\nDoctor: ", end='', flush=True)
                pending_prompt.set()
                last_activity = time.time()
            idle_triggered.clear()

def connect_to_server(scenario):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.sendall(str(scenario).encode('utf-8'))
            patient_name = sock.recv(1024).decode('utf-8').strip()
            return sock, patient_name
        except Exception as e:
            print(f"Connection failed ({e}), retrying in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)

def main():
    global last_activity

    password = getpass.getpass("Enter password to use the client: ")
    if password != "cyberlab":
        print("Incorrect password. Exiting.")
        sys.exit(1)

    print("Available scenarios:")
    for patient in patients:
        print(f"{patient[0]}. {patient[1]}")

    while True:
        try:
            scenario = int(input("Choose scenario (1-16): "))
            if 1 <= scenario <= 16:
                last_activity = time.time()
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            print("Invalid choice. Try again.")
        except ValueError:
            print("Numbers only please.")

    sock, patient_name = connect_to_server(scenario)

    threading.Thread(target=clear_screen_if_inactive, args=(patient_name,), daemon=True).start()
    threading.Thread(target=idle_mumble, args=(sock, patient_name), daemon=True).start()

    last_query = None
    while True:
        try:
            if pending_prompt.is_set():
                with input_lock:
                    query = input().strip()
                    pending_prompt.clear()
            else:
                query = input(f"\nDoctor: ").strip()
            last_activity = time.time()
            if query.lower() == 'exit':
                break

            last_query = query
            try:
                sock.sendall(query.encode('utf-8'))
                response = receive_full_response(sock)
            except (TimeoutError, ConnectionError) as e:
                print(f"\n[Lost connection: {e}] Attempting to reconnect...")
                sock.close()
                sock, patient_name = connect_to_server(scenario)
                print("[Reconnected. Resending your last question.]")
                sock.sendall(last_query.encode('utf-8'))
                response = receive_full_response(sock)
            print(f"\n{patient_name}: {response}")
            last_activity = time.time()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

    sock.close()

if __name__ == '__main__':
    main()

