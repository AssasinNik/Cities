import os
import torch
import sounddevice as sd
import time
import vosk
import sys
import queue

f=open('spisok.txt', encoding='utf-8')
cities=[]
for i in range(1109):
    cities.append((f.readline())[:-1])

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'model.pt'


if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                                   local_file)  

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)
sample_rate = 48000
speaker='kseniya'
text='Приветствую! Давай сыграем в город+а, предлагаю тебе начать...'
audio = model.apply_tts(text=text,
                        speaker=speaker,
                        sample_rate=sample_rate)
print('Приветствую! Давай сыграем в города, предлагаю тебе начать...')

sd.play(audio,sample_rate)
time.sleep(len(audio)/sample_rate)
sd.stop()

model1=vosk.Model('model1')
samplerate1=16000
device1=1

q1=queue.Queue()

k=0
n=1109
z=''
while True:
    def callback(indata,frames,time,status):
        if status:
            print(status,file=sys.stderr)
        q1.put(bytes(indata))
    with sd.RawInputStream(samplerate=samplerate1, blocksize=8000, device=device1, dtype='int16', channels=1, callback=callback):
        rec=vosk.KaldiRecognizer(model1, samplerate1)
        print('Говорите...')
        while True:
            data=q1.get()
            if rec.AcceptWaveform(data):
                city=rec.Result()
                break
    city=city[14:]
    city=city[:-3]
    city=city.capitalize()
    print(city)
    if city in cities:
        bukva=city[-1]
        if bukva=='ь' or bukva=='ъ' or bukva=='ы':
            bukva=city[-2]
        bukva=bukva.upper()
        cities.remove(city)
        n=n-1
        if k!=0:
            if z[-1]=='ь' or z[-1]=='ъ' or z[-1]=='ы':
                if city[0]!=(z[-2].upper()):
                    text='Город не на ту букву'
                    audio = model.apply_tts(text=text,
                                speaker=speaker,
                                sample_rate=sample_rate)
                    print(text)
                    sd.play(audio,sample_rate)
                    time.sleep(len(audio)/sample_rate)
                    sd.stop()
                    continue
            else:
                if city[0]!=(z[-1].upper()):
                    text='Город не на ту букву'
                    audio = model.apply_tts(text=text,
                                speaker=speaker,
                                sample_rate=sample_rate)
                    print(text)
                    sd.play(audio,sample_rate)
                    time.sleep(len(audio)/sample_rate)
                    sd.stop()
                    continue

        for i in range(n):
            if (cities[i])[0]==bukva:
                text=cities[i]
                z=cities[i]
                audio = model.apply_tts(text=text,
                        speaker=speaker,
                        sample_rate=sample_rate)
                print(text)
                sd.play(audio,sample_rate)
                time.sleep(len(audio)/sample_rate)
                sd.stop()
                cities.remove(z)
                n=n-1
                break
                
    else:
        text='Вашего города не существует'
        audio = model.apply_tts(text=text,
                        speaker=speaker,
                        sample_rate=sample_rate)
        print(text)
        sd.play(audio,sample_rate)
        time.sleep(len(audio)/sample_rate)
        sd.stop()
        
    k+=1
