import os
import torch
import sounddevice as sd
import time

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'model.pt'

if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                                   local_file)  

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

text = 'Дарья кушает макароны и мясо'
sample_rate = 48000
speaker='baya'

audio = model.apply_tts(text=text,
                        speaker=speaker,
                        sample_rate=sample_rate)
print(text)

sd.play(audio,sample_rate)
time.sleep(len(audio)/sample_rate)
sd.stop()



