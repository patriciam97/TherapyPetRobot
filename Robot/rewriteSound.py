from scipy.io import wavfile
import wave
import struct
import random
import time
import numpy as np

sampling_rate_normal, audio_normal = wavfile.read(
    '/Users/patriciamilou/Documents/Github/TherapyPetRobot/sounds/labrador-barking-daniel_simon.wav')
# '/home/pi/Documents/TherapyPetRobot/sounds/labrador-barking-daniel_simon.wav')
sampling_rate_scared, audio_scared = wavfile.read(
    '/Users/patriciamilou/Documents/Github/TherapyPetRobot/sounds/crying_dog.wav')
# '/home/pi/Documents/TherapyPetRobot/sounds/crying_dog.wav')
#
# sampling_rate_normal, audio_normal = wavfile.read('sounds/labrador-barking-daniel_simon.wav')
# sampling_rate_scared, audio_scared = wavfile.read('sounds/crying_dog.wav')


def get_random(audio, status):
    length = len(audio)
    min_duration = 300000
    if status >= 5:
        min_duration = 500000
    start = random.randint(0, length)
    while (start+min_duration > length):
        start = random.randint(0, length)
    return audio[start:start+min_duration]


def get_interval_array_elems(sound, interval):
    # delete every interval nth element
    # np arrange creates list with 0 to sound.size with some "interval" [0, interval,2*interval, ...]
    # deletes these indexes
    sound = np.delete(sound, np.arange(0, sound.size, interval))
    return sound


def create_sound(sound, status):
    prev = time.time()
    title = '/Users/patriciamilou/Documents/Github/TherapyPetRobot/soundsound_' + \
        str(status)+'.wav'
    # title = 'sounds/new/sound_'+str(status)+'.wav'
    noise_output = wave.open(title, 'wb')
    noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
    print("Writing the wav file for state "+str(status))

    mapping = {
        0: 1,
        1: 1.2,
        2:  5,
        3: 3,
        4: 1,
        5: 0.9,
        6: 0.6,
    }
    level = mapping[status]
    y = sound[:, 1]
    if status == 5:
        y = get_interval_array_elems(y, 20)
    elif status == 6:
        y = get_interval_array_elems(y, 10)
    # print(time.time() - prev)

    y = y/level
    y = np.clip(y, -32767, 32767)
    y = y.astype(int)
    if status == 0 or status == 1:
        y = np.repeat(y, repeats=3, axis=0)

    buf = struct.pack("{}h".format(len(y)), *y)
    noise_output.writeframes(buf)
    # print(time.time() - prev)
    # print("sounds/new/sound_"+str(status)+".wav updated.")
    noise_output.close()


def get_new_sound(state):
    start = time.time()
    if state >= 0 and state < 2:
        sound = get_random(audio_scared, state)
        # STATE 0 , 1 -> CRYING
    else:
        sound = get_random(audio_normal, state)
        # STATE 2,3,4 -> NORMAL
        # STATE 5,6 -> HYPE
    print("Sample collected")
    create_sound(sound, state)
    end = time.time()
    print(end-start)
