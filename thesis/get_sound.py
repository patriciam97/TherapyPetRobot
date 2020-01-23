from scipy.io import wavfile
import wave,struct,random

# sampling_rate, audio = wavfile.read('/home/pi/Documents/TherapyPetRobot/thesis/sounds/labrador-barking-daniel_simon.wav')
sampling_rate_normal, audio_normal = wavfile.read('sounds/labrador-barking-daniel_simon.wav')
sampling_rate_scared, audio_scared = wavfile.read('sounds/crying_dog.wav')

def get_random(audio,status):
    length = len(audio)
    min_duration = 200000
    if status>=8:
        min_duration = 500000  
    start = random.randint(0, length)
    while (start+min_duration>length):
        start = random.randint(0, length)
    return audio[start:start+min_duration]

def get_interval_array_elems(arr,interval):
    new_arr=[]
    counter = interval
    for num in arr:
        if counter>0:
            new_arr.append(num)
            counter-=1
        else:
            counter = interval
    return(new_arr)

def create_sound(sound,status):
    # title = '/home/pi/Documents/TherapyPetRobot/thesis/sounds/new/sound_'+str(status)+'.wav'
    title = 'sounds/new/sound_'+str(status)+'.wav'
    noise_output = wave.open(title, 'wb')
    noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
    print("Writing the wav file for state "+str(status))

    mapping = {
        0 : 1,
        1 : 1.2,
        2:  1.5,
        3 : 1,
        4 : 7,
        5 : 3,
        6 : 1,
        7 : 3,
        8 : 5,
        9 : 2,
        10 : 1
    }
    level = mapping[status]

    if status == 8:
        sound = get_interval_array_elems(sound,30)
    elif status == 9:
        sound = get_interval_array_elems(sound,15)
    elif status == 10:
        sound = get_interval_array_elems(sound,10)
    # if (status>=8 and status<11):
    #     sound = sound[1::2]

    for x,y in sound:
        y = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)

        # x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
        # # if status == 0 or status == 1 or status == 2:
        #     y = int(x*level) if (int(x*level)<32767 and int(x*level)>-32767) else (-32767 if x <0 else 32767)
        # if status>=0 and status<8:
        #     y = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)
        # elif status>=8 and status<11:
        #     x = int(x/level) if (int(x/level)<32767 and int(x/level)>-32767) else (-32767 if x <0 else 32767)

        packed_value = struct.pack('h', y)

        if status == 0 or status==1:
            noise_output.writeframes(packed_value)
            noise_output.writeframes(packed_value)
        else:
            noise_output.writeframes(packed_value)

    print("sounds/new/sound_"+str(status)+".wav updated.")
    noise_output.close()

def get_new_sound(state):
    if state >=0 and state <4:
        sound = get_random(audio_scared,state)
    else:
        sound = get_random(audio_normal,state)
    print("Sample collected")
    create_sound(sound,state)

