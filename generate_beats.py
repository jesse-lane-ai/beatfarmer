import read_database as read
import process_audio as pa
import random
import tags

def generate_attributes(key=None, tempo_min=None, tempo_max=None):
    if key == None:
        key = random.choice(tags.musical_key_tags)["name"]
        #key = "C","C#","D", "D#","E","F","F#","G","G#","A","A#","B","undetermined"
        

    if tempo_min == None:
        tempo_min = 1

    if tempo_max == None:
        tempo_max = 500

    attributes = [
    {
        "instrument_type": "drums",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": ["undetermined"]
    },
    {
        "instrument_type": "bass",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": [key]
    },
    {
        "instrument_type": "melodic",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": [key]
    },
    {
        "instrument_type": "fx",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": [key]
    },
    {
        "instrument_type": "vocals",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": [key]
    },{
        "instrument_type": "percussion",
        "tempo_min": tempo_min,
        "tempo_max": tempo_max,
        "key_range": [key]
    }
]
    
    return attributes

attributes = generate_attributes()

print(f"Attributes: {attributes}")

song = []

for dict in attributes:
    my_dbaudiofile = read.get_audiofile_by_instrument_tempo_key(dict)
    
    if my_dbaudiofile is not None:
        song.append(my_dbaudiofile)
    else:
        print(f"No matching audio file found. {dict}")

song_timestretched = pa.stretch_audiofiles_to_tempo(song, 90)
song_audiofile_path = pa.mix_audio_files(song_timestretched)
print(f"Here is the path to your new song: {song_audiofile_path}")