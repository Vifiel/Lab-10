import requests
import pyttsx3
import pyaudio as pa
from vosk import Model, KaldiRecognizer
import webbrowser

tts = pyttsx3.init()
rate = tts.getProperty("rate")
tts.setProperty("rate", rate-50)

tts.setProperty("voice", "en")


model = Model(r"C:\Users\Professional\Documents\model\vosk-model-en-us-0.22-lgraph")

recognizer = KaldiRecognizer(model, 16000)

mic = pa.PyAudio()
stream = mic.open(format=pa.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

stream.start_stream()

buffer = {}

while True:
    data = stream.read(3000, exception_on_overflow=False)
    
    if recognizer.AcceptWaveform(data):
        text = recognizer.Result()
        print(text[14:-3])
        text = text.split()
        text = list(map(lambda x: x.replace('"', ''), text))
        print(text)
        
        #finds word in dictionary and adds it to buffer, prints one of the meanings
        if "find" in text:
            ind = text.index("find")
            word = text[ind+1]
            req = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            buffer[word] = req.json()
            if req.status_code != 200:
                print("Couldn't recognize the request")
                continue
            print(f"{word} is a {buffer[word][0]['meanings'][0]['definitions'][0]['definition']}")

        #saves the meaning for last found word
        elif "save" in text:
            file = open("saves.txt", "r+")
            word = list(buffer.keys())[-1]
            file.write(f"{word} is a {buffer[word][0]['meanings'][0]['definitions'][0]['definition']}\n")
            file.close()
        
        #prinst transcription of last found word
        elif "transcript" in text:
            if len(buffer) > 0:
                word = list(buffer.keys())[-1]
                print(f"[{buffer[word][0]['phonetic']}]")
            else:
                print("Nothing to transcript")
        
        #opens link to source of meaning of the last found word
        elif "link" in text:
            if len(buffer) > 0:
                word = list(buffer.keys())[-1]
                webbrowser.open(f"{buffer[word][0]['sourceUrls'][0]}")
            else:
                print("Nothing to find in the Internet")

        #says the meaning of last buffered word
        elif "speak" in text:
            if len(buffer) > 0:
                word = list(buffer.keys())[-1]
                text = f"{word} is a {buffer[word][0]['meanings'][0]['definitions'][0]['definition']}"
                tts.say(text)
                tts.runAndWait()
            else:
                print("Nothing to find in the Internet")



