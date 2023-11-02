import crepe
import numpy as np
import librosa
from math import log2, pow

""" Example usage
crepe_dict = get_pitch_dnn(file_path)
avg_pitch, avg_key, octave = get_average_pitch(crepe_dict)

print(f"Avg Pitch: {avg_pitch} Avg Key: {avg_key}") """

def get_key_and_octave(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n], octave

def get_average_pitch(pitch):
    pitches = []
    confidences_thresh = 0.8
    i = 0
    while i < len(pitch):
        if(pitch[i][2] > confidences_thresh):
            pitches.append(pitch[i][1])
        i += 1
    if len(pitches) > 0:
        average_frequency = np.array(pitches).mean()
        average_key, octave = get_key_and_octave(average_frequency)
    else:
        average_frequency = 0
        average_key = "A"
        octave = 0
    return average_frequency,average_key, octave

def get_pitch_dnn(audio_file):
    # DNN Pitch Detection
    pitch = []
    audio, sr = librosa.load(audio_file)
    num =int(sr/2)
    first_second_of_audio = audio[:num]
    time, frequency, confidence, activation = crepe.predict(first_second_of_audio, sr, model_capacity="tiny", viterbi=True, center=True, step_size=10, verbose=1) # tiny|small|medium|large|full
    i = 0
    while i < len(time):
        pitch.append([time[i],frequency[i],confidence[i]])
        i += 1
    return pitch