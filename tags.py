def get_instrument_tags():
    return instrument_tags

def get_musical_key_tags():
    return musical_key_tags

instrument_tags = [
    {"name": "drums", 
     "keywords": [
        "drum",  
        "cymbal", 
        "ride",
        "kick",
        "snare", "snr",
        "hat",
        "clap",
        "rim", "tom", "fill"
        ]},
    {"name": "bass", 
     "keywords": 
     [
         "bass",
         "sub", "upright", "low end",
         ]},
    {"name": "percussion",
     "keywords":
     [
         "perc", "timpani", "cowbell", "gong", "clave", "castanet", "cajon",
         "conga", "bongo", "wood", "tabla", "guira", "cabasa", "maracas",
         "agogo", "udu", "darbuka", "frame", "pan", "hang", "snap",
         ]},
    {"name": "melodic",
     "keywords":
     [
         "melodic", "synth", "key",
         "melody",
         "bell", "lead",
         "chime", "pad", "drone", "guitar", "gtr", "organ", "clav",
         "pluck", "harmony", "chord", "synth", "piano", "key", "rhode", "marimba",
         "string", "brass", "horn", "violin", "viola", "oboe", "flute",
         "orchestra", "clarinet", "bassoon", "trumpet", "woodwind",
         "trombone", "arp", "harp", "harmonica", "sitar", "xylophone",
         "didgeridoo", "shakuhachi", "erhu", "oud",
         ]},
    {"name": "fx",
     "keywords":
     [
         "fx",
         "effect",
         "ambience",
         "environment", "impact", "swell", "riser", "sweep",
         "field record", "noise", "glitch", "beep", "zap", "laser",
         "nature", "texture"

         ]},
    {"name": "vocals",
     "keywords":
     [
         "voice", "vox",
         "vocal",
         "choir",
         "acapella",
         "male",
         "vocal",
         "chant",
         "speech",
         "talk",
         "narration",
         "laugh",
         ]}
]

musical_key_tags = [
    {"name": "C", "keywords": [" c ", "_c_","b#", "b sharp", "c natural"]},
    {"name": "C#", "keywords": [" c# ", "_c#_", "c sharp", "d flat"]},
    {"name": "D", "keywords": [" d ", "_d_", "d natural"]},
    {"name": "D#", "keywords": [" d# ", "_d#_", "eb", "d sharp", "e flat"]},
    {"name": "E", "keywords": [" e ", "_e_", "e natural", "f flat"]},
    {"name": "F", "keywords": [" f ", "_f_", "e#", "f natural", "e sharp"]},
    {"name": "F#", "keywords": [" f# ", "_f#_", "f sharp", "g flat"]},
    {"name": "G", "keywords": [" g ", "_g_", "g natural"]},
    {"name": "G#", "keywords": [" g# ", "_g#_", "g sharp", "a flat"]},
    {"name": "A", "keywords": [" a ", "_a_", "a natural"]},
    {"name": "A#", "keywords": [" a# ", "_a#_", "a sharp", "b flat"]},
    {"name": "B", "keywords": [" b ", "_b_", "b natural", "c flat"]}
]



