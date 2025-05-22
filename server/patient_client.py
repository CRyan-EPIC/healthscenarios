import socket

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

def main():
    last_five = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        # Receive patient name from server
        patient_name = sock.recv(1024).decode('utf-8').strip()

        while True:
            query = input(f"\Doctor for {patient_name}: ").strip()
            if query.lower() == 'exit':
                break

            # Update memory (not shown to user)
            last_five.append(query)
            if len(last_five) > 5:
                last_five = last_five[-5:]

            sock.sendall(query.encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            print(patient_name+": ")
            print(response)

if __name__ == '__main__':
    main()
