import socket

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

def main():
    last_five = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        print("Connected to patient server.")
        print("Type 'exit' to quit.\n")

        while True:
            # Show memory
            if last_five:
                print("\nLast five things you said:")
                for idx, q in enumerate(last_five[-5:], 1):
                    print(f"{idx}: {q}")
            else:
                print("\nYou haven't said anything yet.")

            # Get user input
            query = input("\nEnter your question for the patient: ").strip()
            if query.lower() == 'exit':
                print("Exiting.")
                break

            # Update memory
            last_five.append(query)
            if len(last_five) > 5:
                last_five = last_five[-5:]

            # Send to server
            sock.sendall(query.encode('utf-8'))

            # Receive and print response
            response = sock.recv(4096).decode('utf-8')
            print("\nResponse from patient:")
            print(response)

if __name__ == '__main__':
    main()
