import RPi.GPIO as GPIO
import time
import math
import azure.cognitiveservices.speech as speechsdk
import os

class SpeechRecognizerHandler:
    def __init__(self, button_pin=19, led_pin=13, timeout_duration=10):
        # GPIO setup
        self.BUTTON_PIN = button_pin
        self.LED_PIN = led_pin
        self.timeout_duration = timeout_duration

        # GPIO.setwarnings(False)
        # GPIO.cleanup()
        # GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set button as input with pull-up resistor
        GPIO.setup(self.LED_PIN, GPIO.OUT)  # Set LED as output

        # PWM setup for LED
        self.led_pwm = GPIO.PWM(self.LED_PIN, 100)  # PWM frequency 100Hz
        self.led_pwm.start(0)

        # Azure Speech configuration
        self.SPEECH_KEY = os.getenv("SPEECH_KEY")
        self.SPEECH_REGION = os.getenv("SPEECH_REGION")
        if not self.SPEECH_KEY or not self.SPEECH_REGION:
            raise ValueError("Environment variables SPEECH_KEY and SPEECH_REGION must be set")

        self.speech_config = speechsdk.SpeechConfig(subscription=self.SPEECH_KEY, region=self.SPEECH_REGION)

        self.is_recording = False
        self.button_pressed = False
        self.button_released = True
        self.start_time = None

    def recognize_speech(self):
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)
        def recognized_callback(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"Recognized: {evt.result.text}")
            elif evt.result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized.")
            elif evt.result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = evt.result.cancellation_details
                print(f"Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation_details.error_details}")

        speech_recognizer.recognized.connect(recognized_callback)

        print("Recording and recognizing speech...")
        speech_recognizer.start_continuous_recognition()
        self.start_time = time.time()

        # Slow breathing LED effect while recording
        while GPIO.input(self.BUTTON_PIN) == GPIO.LOW:
            if time.time() - self.start_time > self.timeout_duration:
                print("Recording timeout reached")
                break
            duty_cycle = (50 * (1 + math.sin(time.time())))  # Oscillate between 0-100 for breathing effect
            self.led_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)

        # Stop recording when button is released or timeout
        speech_recognizer.stop_continuous_recognition()
        self.led_pwm.ChangeDutyCycle(0)  # Turn off LED
        print("Recording stopped")

        # add some action here


    def check_button_state(self):
        if GPIO.input(self.BUTTON_PIN) == GPIO.LOW:  # Button pressed
            if not self.button_pressed and self.button_released:
                self.button_pressed = True
                self.button_released = False
                if not self.is_recording:
                    # Start recording and recognition process
                    self.is_recording = True
                    self.recognize_speech()
                    self.is_recording = False
        else:
            self.button_released = True
            self.button_pressed = False

    def start(self):
        try:
            while True:
                self.check_button_state()
                time.sleep(0.05)  # Reduced sleep time for smoother LED effect
        except KeyboardInterrupt:
            print("Program terminated")
        finally:
            self.cleanup()

    def cleanup(self):
        self.led_pwm.stop()
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    GPIO.setwarnings(False)
    #GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    handler = SpeechRecognizerHandler(button_pin=19, led_pin=13, timeout_duration=10)
    handler.start()
