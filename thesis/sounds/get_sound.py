from scipy.io import wavfile
import wave,struct,random

sampling_rate, audio = wavfile.read('/home/pi/Documents/TherapyPetRobot/thesis/sounds/labrador-barking-daniel_simon.wav')

def get_random(audio,status):
    length = len(audio)
    min_duration = 300000
    if status>=8:
        min_duration = 500000  
    start = random.randint(0, length)
    while (start+min_duration>length):
        start = random.randint(0, length)
    return audio[start:start+min_duration]

def scared(status,sound):
    mapping = {
        0 :8,
        1: 6,
        2: 3
    }
    level = mapping[status]
    for x,y in sound:
        x = int(x*level) if (int(x*level)<32767 and int(x*level)>-32767) else (-32767 if x <0 else 32767)
    return(sound)

def relaxed(status,sound):
    mapping = {
        3 : 1,
        4 : 3,
        5 : 6,
        6 : 8,
        7 : 10,
    }
    level = mapping[status]
    for x,y in sound:
        x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
    return(sound)

def happy(status,sound):
    mapping = {
        8 : sound[1::2],
        9 : sound[1::2],
        10 : sound[1::2],
    }
    sound = mapping[status]
    level = 4
    for x,y in sound:
        x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
    return(sound)


def create_sound(sound,status):
    title = 'new/sound_'+str(status)+'.wav'
    noise_output = wave.open(title, 'w')
    noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
    if status>8: 
        sound = sound[1::2]
    print(len(sound))
    for x,y in sound:
        packed_value = struct.pack('h', y)
        if status == 0 or status==1 or status>=8:
            noise_output.writeframes(packed_value)
            noise_output.writeframes(packed_value)
        else:
            noise_output.writeframes(packed_value)
    print("new/sound_"+status+".wav updated.")
    noise_output.close()

def get_new_sound(state):
    print("here")
    # get random sample from sound 
    sound = get_random(audio,state) 

    switcher_sound = {
        0 : scared(0,sound),
        1 : scared(1,sound),
        2 : scared(2,sound),
        3 : relaxed(3,sound),
        4 : relaxed(4,sound),
        5 : relaxed(5,sound),
        6 : relaxed(6,sound),
        7 : relaxed(7,sound),
        8 : happy (8,sound),
        9 : happy (9,sound),
        10 : happy (10,sound),
    }
    create_sound(switcher_sound[state],state)
    print("Sound for state"+state+" updated.")

