import socket
import threading
import ollama

SERVER_IP = '192.168.1.100'  # Change as needed
SERVER_PORT = 65432

# patients = [...]  # <-- Paste your patients list here

def handle_client_connection(client_socket, patients, model):
    try:
        # Receive scenario number as first message
        scenario_bytes = client_socket.recv(1024)
        scenario_str = scenario_bytes.decode('utf-8').strip()
        scenario = int(scenario_str)
        idx = scenario - 1
        patient_name = patients[idx][1]
        prompt = patients[idx][2]

        # Send patient name as the first message
        client_socket.sendall(patient_name.encode('utf-8'))

        annoyance_level = 0

        while True:
            query = client_socket.recv(1024).decode('utf-8').strip()
            if not query:
                break

            # Detect if the user is ignoring the patient
            if query == "...":
                annoyance_level += 1
                if annoyance_level == 1:
                    mood = "impatient"
                    desc = f"The student is silent and not asking questions. {patient_name} is starting to get {mood} and responds accordingly."
                elif annoyance_level == 2:
                    mood = "annoyed"
                    desc = f"The student continues to ignore {patient_name}. {patient_name} is now {mood} and responds accordingly."
                else:
                    mood = "frustrated"
                    desc = f"{patient_name} feels ignored and is now {mood}. Respond with clear frustration."
                full_prompt = (
                    f"{prompt}\n\n"
                    f"{desc}\n"
                    f"Write {patient_name}'s response showing their {mood} feeling."
                    f"\n{patient_name} answers:"
                )
            else:
                annoyance_level = 0  # Reset if user resumes normal questioning
                full_prompt = (
                    f"{prompt}\n\n"
                    f"Student asks: {query}\n"
                    f"{patient_name} answers:"
                )

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

def select_model():
    model = input("Enter Ollama model to use (e.g., llama3:8b): ").strip()
    if not model:
        model = "llama3"  # Default model if none entered
    return model

def main():
    model = select_model()
    print(f"Using model '{model}'. Waiting for client questions...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(15)
        print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(
                target=handle_client_connection,
                args=(client_socket, patients, model),
                daemon=True
            )
            client_thread.start()

if __name__ == '__main__':
    main()
