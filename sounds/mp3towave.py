from os import path
from pydub import AudioSegment
import numpy as np
# files
src = "heartbeat.mp3"
dst = "heartbeat2.wav"

# convert wav to mp3
sound = AudioSegment.from_mp3(src)
# sound2 = np.asarray((sound.get_array_of_samples()))
# print(np.amax(sound2))
# print(np.amin(sound2))
# print(np.where(sound2 == 26606))
# print(np.where(sound2 == ))
sound = sound[0:7000]
sound=sound+3
sound.export(dst, format="wav")
 