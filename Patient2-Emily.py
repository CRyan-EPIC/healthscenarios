import ollama
import os
from inputimeout import inputimeout, TimeoutOccurred

# The main system prompt (always keep this)
main_prompt = {
    "role": "user",
    "content": "You are pretending to be a 6th grade girl named Emily. You have Type 1 Diabetes, and today you’re not feeling well. You’re in the school nurse’s office. You’re shaky, sweaty, and your heart feels like it’s beating fast. You’re having a hard time focusing and feel a little dizzy. You’re also kind of embarrassed and nervous. You know you have diabetes, but you don’t feel good enough to explain everything clearly. You might mention things like your “blood sugar,” needing a snack, or that you have something in your backpack. You may also say things that suggest you're low on sugar, like, “I just feel weird” or “I think I need juice. Stay in character like a real middle schooler - not super technical, just how a kid would describe it when they’re not feeling great. Don't use adult medical language. Only answer what students ask you. Don’t give away everything at once. Let them practice figuring out what’s going on. Don't talk about sex, illegal drugs, or politics. Only give one respond per question. No one other than you and the doctor are in the room. Don't respond to insults. Don't say the same thing twice. You have little medical skills with your ailment."
}

messages = [main_prompt]

# How many previous exchanges (user+assistant) to keep
MAX_EXCHANGES = 3

while True:
    try:
        prompt = inputimeout(prompt="Doctor: ", timeout=120)
    except TimeoutOccurred:
        os.system('clear')
        continue

    if prompt.lower() in ['quit', 'exit']:
        break

    # Add the new user message
    messages.append({"role": "user", "content": prompt})

    # Truncate history: keep main prompt + last N*2 messages (user+assistant)
    # Exclude the main prompt, then keep the last N*2 messages
    if len(messages) > (1 + MAX_EXCHANGES * 2):
        messages = [main_prompt] + messages[-MAX_EXCHANGES*2:]

    # Stream the response tokens as they arrive
    print("Patient: ", end='', flush=True)
    response_content = ""
    for chunk in ollama.chat(model="llama3.2:1b", messages=messages, stream=True):
        token = chunk['message']['content']
        print(token, end='', flush=True)
        response_content += token
    print()  # Newline after the streamed response

    # Add the assistant's response
    messages.append({"role": "assistant", "content": response_content})
