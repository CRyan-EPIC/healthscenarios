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
            query = input(f"\nDoctor: ").strip()
            if query.lower() == 'exit':
                break

            last_five.append(query)
            if len(last_five) > 5:
                last_five = last_five[-5:]

            sock.sendall(query.encode('utf-8'))

            print(f"\n{patient_name}:")
            # Stream and print tokens as they arrive
            buffer = ""
            while True:
                chunk = sock.recv(64).decode('utf-8')
                buffer += chunk
                if "<<END_OF_RESPONSE>>" in buffer:
                    # Print everything up to the marker
                    print(buffer.replace("<<END_OF_RESPONSE>>", ""), end="", flush=True)
                    break
                print(chunk, end="", flush=True)

if __name__ == '__main__':
    main()
