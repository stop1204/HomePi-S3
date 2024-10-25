# command_writer.py
import os
import base64
import openai
import json
import time
import logging
import sounddevice as sd
import wavio
import threading
import RPi.GPIO as GPIO

# pip install openai sounddevice wavio RPi.GPIO

# Configure logging
log_path = os.path.join("/home","terry", "wifi_configurator", "wifi_configurator.log")

logging.basicConfig(
    # filename='command_writer.log',
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure OpenAI API key
LEPTON_API_TOKEN="xhwg2y4dpim3vqu16z8ijtjxk12e93u6"
# LEPTON_API_TOKEN = os.getenv("LEPTON_API_TOKEN")
if not LEPTON_API_TOKEN:
    raise ValueError("Environment variable LEPTON_API_TOKEN must be set")

client = openai.OpenAI(
    base_url="https://qwen2-72b.lepton.run/api/v1/",
    api_key=LEPTON_API_TOKEN
)



# Define the command file path
COMMAND_FILE = "/home/terry/Desktop/HomePi-S3/lcd_command.txt"  # 根據您的命令處理腳本設置路徑

# Audio recording settings
SAMPLE_RATE = 16000  # Hertz
CHANNELS = 1
RECORD_DURATION = 5  # Seconds
AUDIO_FORMAT = "opus"
BITRATE = 16

# GPIO setup
AI_BUTTON_PIN = 19  # GPIO pin number for the button
AI_LED_PIN = 13     # GPIO pin number for the LED

GPIO.setmode(GPIO.BCM)
GPIO.setup(AI_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set button as input with pull-up resistor
GPIO.setup(AI_LED_PIN, GPIO.OUT)  # Set LED as output
def ai_record_audio(filename):
    """
    Record audio from the microphone and save it to a WAV file.
    """
    logging.info(f"Recording started: {filename}")
    GPIO.output(AI_LED_PIN, GPIO.HIGH)  # Turn on LED to indicate recording
    try:
        recording = sd.rec(int(RECORD_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
        sd.wait()  # Wait until recording is finished
        wavio.write(filename, recording, SAMPLE_RATE, sampwidth=2)
        logging.info(f"Recording finished: {filename}")
        return True
    except Exception as e:
        logging.error(f"Error recording audio: {e}")
        return False
    finally:
        GPIO.output(AI_LED_PIN, GPIO.LOW)  # Turn off LED after recording

def ai_send_audio_to_ai(audio_file_path):
    """
    Send the audio file to AI API for speech recognition and command parsing.
    """
    try:
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()
            audio_data = base64.b64encode(audio_bytes).decode()

        # Define the input and output formats
        format_ = AUDIO_FORMAT
        bitrate = BITRATE

        # Create the API request
        completion = client.chat.completions.create(
            model="qwen2-72b",
            extra_body={
                "tts_audio_format": format_,
                "tts_audio_bitrate": bitrate,
                "require_audio": True,
                "tts_preset_id": "jessica",
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart home assistant. Please convert the user's natural language command from the following audio into a JSON object with 'action' and 'message' fields based on the predefined actions below. Return only the JSON object.\n"
                        "Predefined actions:\n"
                        # "- action: 'display', message: <display message>\n"
                        # "- action: 'clear', message: ''\n"
                        # "- action: 'qr_code', message: ''\n"
                        # "- action: 'unknown', message: ''\n"
                        "- action: '[OPEN_DOOR]', message: ''\n"
                        "- action: '[CLOSE_DOOR]', message: ''\n"
                        "- action: '[TURN_ON_LIGHT]', message: ''\n"
                        "- action: '[TURN_OFF_LIGHT]', message: ''\n"
                        "- action: '[TURN_ON_FAN]', message: ''\n"
                        "- action: '[TURN_OFF_FAN]', message: ''\n"
                        "- action: '[UNKNOWN_COMMAND]', message: ''\n"
                        "Ensure the response is a valid JSON object. If the command does not match any of the above, set 'action' to 'unknown' and 'message' to an empty string."
                    )
                },
                {
                    "role": "user",
                    "content": [{"type": "audio", "data": audio_data}]
                }
            ],
            max_tokens=50,
            temperature=0,
            stream=False  # Set stream to False as per your requirement
        )

        # Extract the command from the response
        if completion.choices and len(completion.choices) > 0:
            message_obj = completion.choices[0].message
            command_json_str = message_obj.content.strip()  # 使用屬性訪問
            logging.info(f"AI Response: {command_json_str}")  # 日誌記錄 AI 的原始回應
            # Validate JSON
            try:
                command = json.loads(command_json_str)
                if 'action' in command and 'message' in command:
                    logging.info(f"Recognized command: {command}")
                    return command
                else:
                    logging.warning("AI response JSON does not contain 'action' and 'message' fields.")
                    return {"action": "unknown", "message": ""}
            except json.JSONDecodeError:
                logging.error("AI response is not valid JSON.")
                return {"action": "unknown", "message": ""}
        else:
            logging.warning("No command recognized from AI API.")
            return {"action": "unknown", "message": ""}

        # Extract the command from the response
        # if completion.choices and len(completion.choices) > 0:
        #     command = completion.choices[0].message['content'].strip()
        #     logging.info(f"Recognized command: {command}")
        #     return command
        # else:
        #     logging.warning("No command recognized from AI API.")
        #     return "[UNKNOWN_COMMAND]"

    except Exception as e:
        logging.error(f"Error sending audio to AI API: {e}")
        return {"action": "unknown", "message": ""}

def ai_write_command(command):
    """
    Write the command to the command file in JSON format.
    """
    try:
        with open(COMMAND_FILE, "w") as file:  # 使用 'w' 模式覆蓋文件，以符合您的命令處理腳本
            json.dump(command, file)
        logging.info(f"Command written to file: {command}")
    except Exception as e:
        logging.error(f"Error writing command to file: {e}")

def ai_process_audio_file(audio_directory, filename):
    """
    Process a single audio file: send to AI and write the command.
    """
    audio_path = os.path.join(audio_directory, filename)
    logging.info(f"Processing audio file: {audio_path}")
    command = ai_send_audio_to_ai(audio_path)
    ai_write_command(command)
    # Optionally, move or delete the processed audio file
    try:
        os.remove(audio_path)
        logging.info(f"Processed and removed audio file: {audio_path}")
    except Exception as e:
        logging.error(f"Error removing audio file '{audio_path}': {e}")

def ai_monitor_button_and_record(audio_directory):
    """
    Monitor the button and record audio when the button is pressed.
    """
    try:
        while True:
            button_state = GPIO.input(AI_BUTTON_PIN)
            if button_state == GPIO.LOW:
                # Button pressed
                timestamp = int(time.time())
                filename = f"audio_{timestamp}.wav"
                audio_path = os.path.join(audio_directory, filename)
                success = ai_record_audio(audio_path)
                if success:
                    ai_process_audio_file(audio_directory, filename)
                # Debounce to prevent multiple recordings
                time.sleep(1)
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("command_writer.py terminated by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        GPIO.cleanup()

def main():
    """
    Main function to start the command writer.
    """
    AUDIO_DIRECTORY = "/home/terry/audio_files"  # Replace with your actual audio files directory

    if not os.path.exists(AUDIO_DIRECTORY):
        os.makedirs(AUDIO_DIRECTORY)
        logging.info(f"Created audio directory: {AUDIO_DIRECTORY}")

    logging.info("Starting command_writer.py...")

    # Start monitoring the button and recording audio in the main thread
    ai_monitor_button_and_record(AUDIO_DIRECTORY)

if __name__ == "__main__":
    main()