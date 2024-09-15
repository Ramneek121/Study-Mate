import serial
import time
import requests
import pygame
import speech_recognition as sr
import os

# === Configuration ===

# Serial Configuration
SERIAL_PORT = 'COM9'  # Replace with your Arduino's COM port (e.g., 'COM3' for Windows or '/dev/ttyACM0' for Linux)
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

# OpenAI (ChatGPT) Configuration
OPENAI_API_KEY = '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'  # Replace with your OpenAI API key
OPENAI_URL = 'https://api.openai.com/v1/chat/completions'  # For GPT-3.5 or GPT-4

# ElevenLabs Configuration
ELEVENLABS_API_KEY = 'sk_c996c93ea31f008cf5a0b6abeadffee402debdb30fd0b605'  # Replace with your ElevenLabs API key
ELEVENLABS_VOICE_ID = 'tnSpp4vdxKPjI9w0GnoV'  # Replace with your chosen voice ID from ElevenLabs
ELEVENLABS_URL = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}'

# Voiceflow Configuration
VOICEFLOW_API_KEY = 'VF.DM.66e6140b380effe3d506dec7.aqDeagnGEzB2xRd5'  # Replace with your Voiceflow API key
VOICEFLOW_USER_ID = 'your_unique_user_id'  # Replace with a unique identifier for the user/session
VOICEFLOW_URL = f'https://general-runtime.voiceflow.com/state/{VOICEFLOW_USER_ID}/dialog'

# Headers for APIs
OPENAI_HEADERS = {
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'Content-Type': 'application/json'
}

ELEVENLABS_HEADERS = {
    'xi-api-key': ELEVENLABS_API_KEY,
    'Content-Type': 'application/json'
}

VOICEFLOW_HEADERS = {
    'Authorization': VOICEFLOW_API_KEY,
    'Content-Type': 'application/json'
}

# Initialize Pygame Mixer
pygame.mixer.init()

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

# Initialize Serial Connection
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
    time.sleep(2)  # Wait for Arduino to initialize
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

def listen_voice():
    """
    Captures voice input from the microphone and converts it to text using SpeechRecognition.
    """
    with sr.Microphone() as source:
        print("Listening for voice input...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Voice Input: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Speech Recognition service; {e}")
        return None

def get_voiceflow_response(user_input):
    """
    Sends user input to Voiceflow and retrieves the response.
    """
    data = {
        "type": "text",
        "payload": {
            "text": user_input
        }
    }
    try:
        response = requests.post(VOICEFLOW_URL, headers=VOICEFLOW_HEADERS, json=data)
        if response.status_code == 200:
            voiceflow_response = response.json()['payload']['text'].strip()
            print(f"Voiceflow Response: {voiceflow_response}")
            return voiceflow_response
        else:
            print(f"Voiceflow API Error: {response.status_code} - {response.text}")
            return "I'm sorry, I couldn't process that."
    except Exception as e:
        print(f"Error communicating with Voiceflow: {e}")
        return "I'm sorry, I couldn't process that."

def get_chatgpt_response(prompt):
    """
    Sends a prompt to OpenAI's ChatGPT and returns the response.
    """
    data = {
        "model": "gpt-4",  # or "gpt-3.5-turbo"
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
        "temperature": 0.7
    }
    try:
        response = requests.post(OPENAI_URL, headers=OPENAI_HEADERS, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"OpenAI API Error: {response.status_code} - {response.text}")
            return "I'm sorry, I couldn't process that."
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        return "I'm sorry, I couldn't process that."

def text_to_speech_elevenlabs(text):
    """
    Converts text to speech using ElevenLabs and saves the audio file.
    """
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",  # Choose the appropriate model
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
response = requests.post(ELEVENLABS_URL, headers=ELEVENLABS_HEADERS, json=data)
audio_file_path = ''

     try:
        response = requests.post(ELEVENLABS_URL, headers=ELEVENLABS_HEADERS, json=data)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Delete the existing audio file if it exists
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            logging.info(f"Existing audio file '{audio_file_path}' deleted.")

        # Write the new audio content to the file
        with open(audio_file_path, 'wb') as audio_file:
            audio_file.write(response.content)
        print(f"Audio file generated by ElevenLabs: {audio_file_path}")
        logging.info(f"Audio file generated: {audio_file_path}")
        return audio_file_path  

except requests.exceptions.HTTPError as http_err:
        print(f"ElevenLabs API HTTP Error: {http_err}")
        logging.error(f"ElevenLabs API HTTP Error: {http_err}")
        return None



def play_audio(file_path):
    """
    Plays the audio file using pygame.
    """
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("Playing audio...")
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)  # Wait for the audio to finish playing
    except Exception as e:
        print(f"Error playing audio: {e}")

def send_to_arduino(message):
    """
    Sends a message to Arduino via serial.
    """
    try:
        arduino.write((message + '\n').encode('utf-8'))
        print(f"Sent to Arduino: {message}")
    except Exception as e:
        print(f"Error sending to Arduino: {e}")

def receive_from_arduino():
    """
    Listens for messages from Arduino.
    """
    if arduino.in_waiting > 0:
        try:
            message = arduino.readline().decode('utf-8').strip()
            print(f"Received from Arduino: {message}")
            return message
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            return None
    return None

def main():
    """
    Main loop to handle voice input and API interactions.
    """
    try:
        while True:
            # Capture voice input
            user_voice = listen_voice()
            if user_voice:
                # Send to Voiceflow for processing
                voiceflow_response = get_voiceflow_response(user_voice)
                
                # Optionally, send Voiceflow's response to ChatGPT for further processing
                chatgpt_response = get_chatgpt_response(voiceflow_response)
                
                # Send response back to Arduino
                send_to_arduino(chatgpt_response)
                
                # Convert response to speech using ElevenLabs
                audio_file = text_to_speech_elevenlabs(chatgpt_response)
                if audio_file:
                    play_audio(audio_file)
            
            # Optionally, listen for messages from Arduino
            arduino_message = receive_from_arduino()
            if arduino_message:
                # You can handle Arduino messages here
                pass
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        arduino.close()
        pygame.mixer.quit()
        print("Serial connection closed and pygame mixer quit.")

if __name__ == "__main__":
    main()
