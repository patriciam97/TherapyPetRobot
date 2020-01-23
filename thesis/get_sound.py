from scipy.io import wavfile
import wave,struct,random

sampling_rate, audio = wavfile.read('/home/pi/Documents/TherapyPetRobot/thesis/sounds/labrador-barking-daniel_simon.wav')

def get_random(audio,status):
    length = len(audio)
    min_duration = 600000
    # if status>=8:
    #     min_duration = 500000  
    start = random.randint(0, length)
    while (start+min_duration>length):
        start = random.randint(0, length)
    return audio[start:start+min_duration]

# def scared(status,sound):
#     mapping = {
#         0 :8,
#         1: 6,
#         2: 3
#     }
#     level = mapping[status]
#     print("Editing for scared level "+str(status))
#     for x,y in sound:
#         x = int(x*level) if (int(x*level)<32767 and int(x*level)>-32767) else (-32767 if x <0 else 32767)
#     return(sound)

# def relaxed(status,sound):
#     mapping = {
#         3 : 1,
#         4 : 3,
#         5 : 6,
#         6 : 8,
#         7 : 10,
#     }
#     level = mapping[status]
#     print("Editing for relaxed level "+str(status))
#     for x,y in sound:
#         x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
#     return(sound)

# def happy(status,sound):
#     mapping = {
#         8 : sound[1::2],
#         9 : sound[1::2],
#         10 : sound[1::2],
#     }
#     sound = mapping[status]
#     level = 4
#     print("Editing for happy level "+str(status))
#     for x,y in sound:
#         x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
#     return(sound)


def create_sound(sound,status):
    title = '/home/pi/Documents/TherapyPetRobot/thesis/sounds/new/sound_'+str(status)+'.wav'
    noise_output = wave.open(title, 'wb')
    noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
    if status>8: 
        sound = sound[1::2]
    print("Writing the wav file for state "+str(status))

    mapping = {
        0 :8,
        1: 6,
        2: 3,
        3 : 1,
        4 : 3,
        5 : 6,
        6 : 8,
        7 : 10,
        8 : 4,
        9 : 4,
        10 : 4
    }
    level = mapping[status]

    if status>=8 and status<11:
        sound = sound[1::2]

    for x,y in sound:

        if status == 0 or status == 1 or status == 2:
            y = int(x*level) if (int(x*level)<32767 and int(x*level)>-32767) else (-32767 if x <0 else 32767)
        elif status>2 and status<8:
            y = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
        elif status>=8 and status<11:
            x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)

        packed_value = struct.pack('h', y)

        if status == 0 or status==1 or status>=8:
            noise_output.writeframes(packed_value)
            noise_output.writeframes(packed_value)
        else:
            noise_output.writeframes(packed_value)
    print("sounds/new/sound_"+str(status)+".wav updated.")
    noise_output.close()

def get_new_sound(state):
    # get random sample from sound 
    sound = get_random(audio,state)
    print("Sample collected")
    # switcher_sound = {
    #     0 : scared(0,sound),
    #     1 : scared(1,sound),
    #     2 : scared(2,sound),
    #     3 : relaxed(3,sound),
    #     4 : relaxed(4,sound),
    #     5 : relaxed(5,sound),
    #     6 : relaxed(6,sound),
    #     7 : relaxed(7,sound),
    #     8 : happy (8,sound),
    #     9 : happy (9,sound),
    #     10 : happy (10,sound),
    # }
    create_sound(sound,state)

