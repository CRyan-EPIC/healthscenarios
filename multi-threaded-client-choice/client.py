import socket
import os
import threading
import time
import sys
import getpass

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432
SOCKET_TIMEOUT = 30
RECONNECT_DELAY = 3
IDLE_TIMEOUT = 60  # seconds

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

last_activity = time.time()
idle_lock = threading.Lock()
idle_triggered = threading.Event()

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
    while True:
        sock, patient_name = connect_to_server(scenario)
        try:
            sock.sendall(last_query.encode('utf-8'))
            response = receive_full_response(sock)
            return sock, patient_name, response
        except Exception as e:
            print(f"[Resend failed after reconnect: {e}] Retrying...")
            sock.close()
            time.sleep(RECONNECT_DELAY)

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

def idle_mumble_thread(sock_ref, patient_name_ref, scenario_ref):
    global last_activity
    while True:
        time.sleep(1)
        if idle_triggered.is_set():
            continue
        if time.time() - last_activity > IDLE_TIMEOUT:
            idle_triggered.set()
            with idle_lock:
                try:
                    sock = sock_ref[0]
                    patient_name = patient_name_ref[0]
                    scenario = scenario_ref[0]
                    sock.sendall("...".encode('utf-8'))
                    response = receive_full_response(sock)
                except Exception as e:
                    print(f"\n[Idle mumble failed: {e}] Attempting to reconnect...")
                    sock, patient_name, response = reconnect_and_resend(scenario, "...")
                    sock_ref[0] = sock
                    patient_name_ref[0] = patient_name
                print(f"\n{patient_name_ref[0]}: {response}")
                print("\nDoctor: ", end='', flush=True)
                last_activity = time.time()
            idle_triggered.clear()

def main():
    global last_activity
    password = getpass.getpass("Enter password to use the client: ")
    if password != "cyberlab":
        print("Incorrect password. Exiting.")
        sys.exit(1)

    scenario = choose_scenario()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Choose scenario (1-16): {scenario}")

    sock, patient_name = connect_to_server(scenario)
    last_query = None

    # For mutable references in the idle thread
    sock_ref = [sock]
    patient_name_ref = [patient_name]
    scenario_ref = [scenario]

    threading.Thread(target=idle_mumble_thread, args=(sock_ref, patient_name_ref, scenario_ref), daemon=True).start()

    while True:
        try:
            query = input("\nDoctor: ").strip()
            last_activity = time.time()
            if query.lower() == 'exit':
                break
            if query.lower() == '.switch':
                sock.close()
                scenario = choose_scenario()
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"Choose scenario (1-16): {scenario}")
                sock, patient_name = connect_to_server(scenario)
                # Update references for idle thread
                sock_ref[0] = sock
                patient_name_ref[0] = patient_name
                scenario_ref[0] = scenario
                continue
            last_query = query
            while True:
                try:
                    sock.sendall(query.encode('utf-8'))
                    response = receive_full_response(sock)
                    break  # Success, break inner loop
                except (TimeoutError, ConnectionError) as e:
                    print(f"\n[Lost connection: {e}] Attempting to reconnect...")
                    sock.close()
                    sock, patient_name, response = reconnect_and_resend(scenario, last_query)
                    print("[Reconnected. Resending your last question.]")
                    # Update references for idle thread
                    sock_ref[0] = sock
                    patient_name_ref[0] = patient_name
            print(f"\n{patient_name}: {response}")
            idle_triggered.clear()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

    sock.close()

if __name__ == '__main__':
    main()
