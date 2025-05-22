# Client code remains identical to original
import socket

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

def main():
    query = input("Enter your question for the patient: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(query.encode('utf-8'))

        response = sock.recv(4096).decode('utf-8')
        print("Response from patient:")
        print(response)

if __name__ == '__main__':
    main()
