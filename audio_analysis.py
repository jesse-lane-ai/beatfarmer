import librosa
import numpy as np
import re
import tags
from msclap import CLAP
import torch.nn.functional as F
import sys
import utilities
import audio_pitch_estimation as ape


def analyze(audio_file_path):
    print(audio_file_path)
    if check_duration(audio_file_path):
        print(f"Audio file path: {audio_file_path}")
        return extract_audio_attributes(audio_file_path)

def check_duration(audio_file_path, min_duration=3.0, max=24.0):
    """
    Check the duration of an audio file to see if it falls within a specified range.

    Parameters:
    - audio_file_path (str): The path to the audio file to be checked.
    - min_duration (float, optional): The minimum allowable duration in seconds (default is 6.0 seconds).
    - max_duration (float, optional): The maximum allowable duration in seconds (default is 18.0 seconds).

    Returns:
    - bool: True if the audio file duration is within the specified range, False otherwise.

    This function loads an audio file using the Librosa library and calculates its duration.
    It then compares the duration to the specified minimum and maximum values.
    If the duration falls within the specified range, the function returns True; otherwise, it returns False.
    If any exceptions occur during the process, an error message is printed, and False is returned.
    """
    check = False

    try:
        # Load the audio file
        y, sr = librosa.load(audio_file_path, sr=None)
        
        # Get the duration of the audio
        duration = librosa.get_duration(y=y, sr=sr)
        print(duration)
        # Check if the duration is less than the threshold
        if duration > min_duration:
            
            if duration < max:
                check = True

        return check
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def extract_audio_attributes(file_path):
    # Initialize attributes with "undetermined"
    attributes = {
        "musical_key": "undetermined",
        "tempo": None,
        "instrument_type": "undetermined",
        "length_in_samples": None,
        "sample_rate": None,
    }

    y, sr = librosa.load(file_path, sr=None)

    attributes["sample_rate"] = sr
    attributes["length_in_samples"] = len(y)

    # Searching for tempo: Assume it is a number between 50 and 240
    tempo_match = re.search(r"([5-9]\d|1\d\d|2[0-3]\d|240)", file_path)
    if tempo_match:
        attributes["tempo"] = float(tempo_match.group(1))
    else:
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        attributes["tempo"] = float(tempo)

    instrument_tags = tags.get_instrument_tags()
    musical_key_tags = tags.get_musical_key_tags()
        
    # Check path segments for possible instrument type info
    path_segments = file_path.split("\\")
    
    instrument_found = False
    for segment in path_segments:
        
        for tag in instrument_tags:
            
            for keyword in tag["keywords"]:
                if re.search(keyword, segment, re.IGNORECASE):
                    
                    attributes["instrument_type"] = tag["name"]
                    
                    instrument_found = True
                    break 
            if instrument_found:
                break 
        if instrument_found:
            #print("attributes[instrument_type] != undetermined Ran")
            break         

    if attributes["instrument_type"] == "undetermined":
        attributes["instrument_type"] = utilities.time_function_execution(neural_instrument_categorize, file_path)

    print(f"Music Category: {attributes['instrument_type']}")

    for segment in path_segments:
        # Check for musical key
        for key in musical_key_tags:
            for keyword in key["keywords"]:
                if keyword in segment.lower():
                    attributes["musical_key"] = key["name"]
                    break  # exit the inner loop once a key is found
            if attributes["musical_key"] != "undetermined":
                break  # exit the outer loop once a key is found

    if attributes["musical_key"] == "undetermined":
        if attributes["instrument_type"] != "drums":
                    crepe_dict = ape.get_pitch_dnn(file_path)
                    avg_pitch, avg_key, octave = ape.get_average_pitch(crepe_dict)
                    attributes["musical_key"] = avg_key

    print(f"Musical Key: {attributes['musical_key']}")

    return attributes

def neural_instrument_categorize(audio_file):
    """
    Categorizes a given audio file into one of the predefined musical instrument classes.

    Utilizes the CLAP neural model (2023 version) to determine the category of the provided 
    audio file based on its content. The function computes embeddings for the audio file and 
    compares them with embeddings generated from predefined class prompts.

    Parameters:
    - audio_file (str): Path to the audio file to be categorized.

    Returns:
    - str: The top predicted category for the audio file, chosen from the following classes:
      "drums", "bass", "percussion", "fx", "melodic", "vocals".

    Note:
    This function assumes that the CLAP model and necessary dependencies are already imported 
    and available in the current environment.

    Example:
    >>> result = neural_instrument_categorize("path_to_audio_file.wav")
    >>> print(result)
    'drums'
    """
    # Define classes for zero-shot
    # Should be in lower case and can be more than one word
    classes = ["drums", "bass", "percussion", "fx", "melodic", "vocals"]
    ground_truth = ['drums']
    # Add prompt
    prompt = 'this type of musical sound is '
    class_prompts = [prompt + x for x in classes]

    #Load audio files
    audio_files = []
    audio_files.append(audio_file)

    # Setting use_cuda = True will load the model on a GPU using CUDA
    clap_model = CLAP(version = '2023', use_cuda=True)

    # compute text embeddings from natural text
    text_embeddings = clap_model.get_text_embeddings(class_prompts)

    audio_embeddings = clap_model.get_audio_embeddings(audio_files, resample=True)
    #print(f"audio_embeddings: {audio_embeddings}")
    
    # compute the similarity between audio_embeddings and text_embeddings
    similarity = clap_model.compute_similarity(audio_embeddings, text_embeddings)

    similarity = F.softmax(similarity, dim=1)
    values, indices = similarity[0].topk(6)

    """ #Print the results
    print("Ground Truth: {}".format(ground_truth))
    print("Top predictions:/n")
    for value, index in zip(values, indices):
        print(f"{classes[index]:>16s}: {100 * value.item():.2f}%") """
    
    #print(f"return: {classes[indices[0]]}")
    return classes[indices[0]]

def root_mean_square(data):
    """
    Compute the Root Mean Square (RMS) value of a given data.
    
    Args:
        data (numpy.array): Input audio data as a numpy array.
        
    Returns:
        float: RMS value of the provided audio data.
    """
    return float(np.sqrt(np.mean(np.square(data))))

def loudness_of(data):
    """
    Calculate the loudness of the provided audio data using RMS.
    
    Args:
        data (numpy.array): Input audio data as a numpy array.
        
    Returns:
        float: Loudness of the provided audio data.
    """
    return root_mean_square(data)

def normalized(list):
    """
    Normalize an audio buffer so that the loudest value is scaled to 1.0.
    
    Args:
        list (numpy.array): Audio buffer as a numpy array.
        
    Returns:
        numpy.array: Normalized audio data.
    """
    """Given an audio buffer, return it with the loudest value scaled to 1.0"""
    return list.astype(np.float32) / float(np.amax(np.abs(list)))

neg80point8db = 0.00009120108393559096
bit_depth = 16
default_silence_threshold = (neg80point8db * (2 ** (bit_depth - 1))) * 4

def start_of(list, threshold=default_silence_threshold, samples_before=1):
    """
    From https://github.com/samim23/polymath
    Find the start index of significant audio data by comparing against a given threshold.
    
    Args:
        list (numpy.array): Audio data as a numpy array.
        threshold (float, optional): Silence threshold. Defaults to default_silence_threshold.
        samples_before (int, optional): Number of samples to return before the threshold is exceeded. Defaults to 1.
        
    Returns:
        int: Start index of significant audio data.
    """
    if int(threshold) != threshold:
        threshold = threshold * float(2 ** (bit_depth - 1))
    index = np.argmax(np.absolute(list) > threshold)
    if index > (samples_before - 1):
        return index - samples_before
    else:
        return 0

def end_of(list, threshold=default_silence_threshold, samples_after=1):
    """
    From https://github.com/samim23/polymath
    Find the end index of significant audio data by comparing against a given threshold.
    
    Args:
        list (numpy.array): Audio data as a numpy array.
        threshold (float, optional): Silence threshold. Defaults to default_silence_threshold.
        samples_after (int, optional): Number of samples to return after the last significant audio data. Defaults to 1.
        
    Returns:
        int: End index of significant audio data.
    """
    if int(threshold) != threshold:
        threshold = threshold * float(2 ** (bit_depth - 1))
    rev_index = np.argmax(
        np.flipud(np.absolute(list)) > threshold
    )
    if rev_index > (samples_after - 1):
        return len(list) - (rev_index - samples_after)
    else:
        return len(list)

def trim_data(
    data,
    start_threshold=default_silence_threshold,
    end_threshold=default_silence_threshold
):
    """
    From https://github.com/samim23/polymath
    Trim audio data by removing leading and trailing silent regions.
    
    Args:
        data (numpy.array): Audio data to be trimmed.
        start_threshold (float, optional): Silence threshold for start of audio data. Defaults to default_silence_threshold.
        end_threshold (float, optional): Silence threshold for end of audio data. Defaults to default_silence_threshold.
        
    Returns:
        numpy.array: Trimmed audio data.
    """
    start = start_of(data, start_threshold)
    end = end_of(data, end_threshold)

    return data[start:end]

def load_and_trim(file):
    """
    From https://github.com/samim23/polymath
    Load an audio file and trim the silent regions.
    
    Args:
        file (str): Path to the audio file.
        
    Returns:
        tuple: Trimmed audio data and its corresponding sample rate.
    """
    y, rate = librosa.load(file, mono=True)
    y = normalized(y)
    trimmed = trim_data(y)
    return trimmed, rate

def get_loudness(file):
    """
    From https://github.com/samim23/polymath
    Compute the loudness of an audio file after loading and trimming.
    
    Args:
        file (str): Path to the audio file.
        
    Returns:
        float: Loudness of the provided audio file.
    """
    loudness = -1
    try:
        audio, rate = load_and_trim(file)
        loudness = loudness_of(audio)
    except Exception as e:
        sys.stderr.write(f"Failed to run on {file}: {e}\n")
    return loudness

def get_volume(file):
    """
    From https://github.com/samim23/polymath
    Compute the volume, average volume, and loudness of an audio file after loading and trimming.
    
    Args:
        file (str): Path to the audio file.
        
    Returns:
        tuple: Volume, average volume, and loudness of the provided audio file.
    """
    volume = -1
    avg_volume = -1
    try:
        audio, rate = load_and_trim(file)
        volume = librosa.feature.rms(y=audio)[0]
        avg_volume = np.mean(volume)
        loudness = loudness_of(audio)
    except Exception as e:
        sys.stderr.write(f"Failed to get Volume and Loudness on {file}: {e}\n")
    return volume, avg_volume, loudness