import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract
import pyttsx3
import cv2
import os
import speech_recognition as sr
import threading

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    if file_path:
        process_image(file_path)

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite("captured_image.png", frame)
        process_image("captured_image.png")
        os.remove("captured_image.png")

def process_image(file_path):
    text = extract_text_from_image(file_path)
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, text)
    read_text_aloud()

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def read_text_aloud():
    text = text_box.get("1.0", tk.END).strip()
    if text:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        text_to_speak = "No text to read aloud."
        engine = pyttsx3.init()
        engine.say(text_to_speak)
        engine.runAndWait()

def set_custom_style():
    button_font = ("Helvetica", 12, "bold")
    label_font = ("Helvetica", 12)

    select_button.config(font=button_font)
    capture_button.config(font=button_font)
    read_button.config(font=button_font)
    text_label.config(font=label_font)
    text_box.config(font=label_font)
    quit_button.config(font=button_font)

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_for_commands():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        n = 1
        while n == 1:
            speak_text("Listening for commands...")
            print("Listening for commands...")
            audio = recognizer.listen(source)
            
            try:
                command = recognizer.recognize_google(audio).lower()
                print("You said:", command)
                speak_text(f"You said: {command}")

                if "google" in command:
                    capture_image()

                elif "select image" in command:
                    select_image()

                elif "read aloud" in command:
                    read_text_aloud()

                elif "correct" in command:
                    root.quit()
                    n = 0
                    break

            except sr.UnknownValueError:
                print("Could not understand audio.")
                speak_text("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Error accessing Google Speech Recognition service: {e}")
                speak_text(f"Error accessing Google Speech Recognition service: {e}")

def get_voice_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak_text(prompt)
        print(prompt)
        audio = recognizer.listen(source)
        
        try:
            response = recognizer.recognize_google(audio).lower()
            print("User response:", response)
            return response
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Error accessing Google Speech Recognition service: {e}")
    
    return None

def on_user_input():
    while True:
        response = get_voice_input("Are you visually impaired? Please say Yes or No.")
        if response and ("yes" in response or "no" in response):
            break

    if "yes" in response:
        start_listening_thread()
    else:
        pass 

def start_listening_thread():
    global command_thread
    command_thread = threading.Thread(target=listen_for_commands)
    command_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("OCR")
    root.geometry("400x400")

    select_button = tk.Button(root, text="Select Image", command=select_image)
    select_button.pack(pady=10)

    capture_button = tk.Button(root, text="Capture Image", command=capture_image)
    capture_button.pack(pady=5)

    read_button = tk.Button(root, text="Read Aloud", command=read_text_aloud)
    read_button.pack(pady=5)

    text_label = tk.Label(root, text="Extracted Text:")
    text_label.pack(pady=5)

    text_box = tk.Text(root, wrap="word", height=10)
    text_box.pack(padx=10, pady=5)

    quit_button = tk.Button(root, text="Quit", command=root.quit)
    quit_button.pack(pady=10)

    on_user_input()

    root.mainloop()
    set_custom_style()
