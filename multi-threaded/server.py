import socket
import threading
import ollama

SERVER_IP = '192.168.1.100'
SERVER_PORT = 65432

# ... (your patients list and scenario/model selection code here)

def handle_client_connection(client_socket, prompt, patient_name, model):
    try:
        # Send patient name as the first message
        client_socket.sendall(patient_name.encode('utf-8'))
        while True:
            query = client_socket.recv(1024).decode('utf-8').strip()
            if not query:
                break

            full_prompt = f"{prompt}\n\nStudent asks: {query}\n{patient_name} answers:"
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            for chunk in stream:
                token = chunk['message']['content']
                client_socket.sendall(token.encode('utf-8'))
            client_socket.sendall(b"<<END_OF_RESPONSE>>")
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        client_socket.sendall(error_msg.encode('utf-8'))
    finally:
        client_socket.close()

def main():
    idx, patient_name, prompt = select_scenario()
    model = select_model()
    print(f"Scenario '{patient_name}' selected. Using model '{model}'. Waiting for client questions...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(15)  # backlog of 15 connections
        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            # Start a new thread for each client
            client_thread = threading.Thread(
                target=handle_client_connection,
                args=(client_socket, prompt, patient_name, model),
                daemon=True  # so threads exit when main thread exits
            )
            client_thread.start()

if __name__ == '__main__':
    main()
