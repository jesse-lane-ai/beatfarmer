import soundfile as sf
import pyrubberband as pyrb
import numpy as np
import os
from audiofile import AudioFile
import resampy
from datetime import datetime
import shutil
import audio_analysis as aa

def multiplication_factor(a: float, b: float) -> float:
    """
    Compute the factor by which `a` must be multiplied to get `b`.

    Args:
    - a (Union[float, int]): The first number.
    - b (Union[float, int]): The second number.

    Returns:
    - float: The multiplication factor.
    """
    if a == 0 and b == 0:
        return 1.0
    elif a == 0:
        raise ValueError("Cannot determine factor when the first value is zero and the second is non-zero.")
    
    return b / a

def reduce_rms(audio_data, db_amount):
    """
    Decrease the amplitude of the audio data to achieve -3dB RMS.
    
    Args:
        audio_data (numpy.array): Input audio data as a numpy array.
        
    Returns:
        numpy.array: Modified audio data with reduced RMS.
    """
    
    # Calculate the current RMS
    current_rms = aa.root_mean_square(audio_data)
    
    # Calculate the desired RMS
    desired_rms = current_rms * 10**(db_amount/20)
    
    # Calculate the scale factor
    scale_factor = desired_rms / current_rms
    
    # Scale the audio data
    adjusted_audio_data = audio_data * scale_factor
    
    return adjusted_audio_data

def time_stretch_audiofile(audiofile_obj, current_tempo, target_tempo):
    output_dir = "./temp"
    factor = multiplication_factor(current_tempo,target_tempo)

    try:
        y, sr = sf.read(audiofile_obj.absolute_path)

        y_stretch = pyrb.time_stretch(y, sr, factor)

        new_filename = f"{audiofile_obj.filename}_stretched"

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        relative_path = f"{output_dir}/{new_filename}.wav"

        sf.write(relative_path, y_stretch, sr)

        current_directory = os.getcwd()

        return AudioFile(
                filename=new_filename,
                file_type="wav",
                absolute_path=f"{current_directory}/{relative_path}",
                directory_path=f"{current_directory}",
                key=audiofile_obj.key,
                tempo=target_tempo,
                instrument_type=audiofile_obj.instrument_type,
                length_in_samples=len(y_stretch),
                sample_rate=sr,
            )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def resample_audio(filepath, target_sample_rate, new_filename):
    output_dir = "./temp"
    
    try:
        # Read the audio file
        y, sr = sf.read(filepath)

        # If the sample rate is already the target, no need to resample
        if sr == target_sample_rate:
            return filepath

        # Resample the audio to the target sample rate
        y_resampled = resampy.resample(y, sr, target_sample_rate)

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        temp_path = f"{output_dir}/{new_filename}"
        # Write the resampled audio to the output path
        sf.write(temp_path, y_resampled, target_sample_rate)

        return temp_path
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def stretch_audiofiles_to_tempo(audiofiles, target_tempo):
    stretched_files = []

    
    for audiofile in audiofiles:
        try:
            current_tempo = audiofile.tempo
            stretched_file = time_stretch_audiofile(audiofile, current_tempo, target_tempo)
            stretched_files.append(stretched_file)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    return stretched_files

def mix_audio_files(audiofile_objects):
    raw_audio_data_list, audio_paths, target_samplerate, target_tempo, target_length, key = prep_audio_files(audiofile_objects)
    
    columns = 2    # For stereo audio signal

    # Initialize audio_data with the desired length and channels
    audio_data = np.zeros((target_length, columns))
    
    # mix subsequent audio files
    for new_data in raw_audio_data_list:
        # Check if new_data is shorter than the target_length
        if new_data.shape[0] < target_length:
       
            # Calculate the amount to repeat the new_data
            difference = target_length - new_data.shape[0]
          
            repeat_times = (difference // new_data.shape[0]) + 1
      
            repeated_data = np.tile(new_data, (repeat_times, 1))
      
            # Trim the repeated_data to match the target_length
            new_data = repeated_data[:target_length, :]

        # If new_data is longer than the target_length, trim it
        elif new_data.shape[0] > target_length:
            new_data = new_data[:target_length, :]

        # Perform element-wise addition
        audio_data = audio_data + new_data

    audio_data = np.tile(audio_data, (3, 1))
    
    now = datetime.now()
    formatted_date = now.strftime('%Y%m%d%H%M%S')
    output_dir = "./output"
    output_path = f"{output_dir}/mixed_audio_{formatted_date}_{key}_{target_tempo}.wav"

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try: 
        sf.write(output_path, audio_data, target_samplerate)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    copy_audio_files(audio_paths, formatted_date)

    return output_path

def prep_audio_files(audiofile_objects):
    audio_paths = []
    raw_audio_data = []

    if not audiofile_objects:
        raise ValueError("The list of audio file objects is empty.")

    try:
        data, samplerate = sf.read(audiofile_objects[0].absolute_path)
        target_samplerate = samplerate
        target_tempo = audiofile_objects[0].tempo
        
        key = audiofile_objects[2].key

        audio_paths.append(audiofile_objects[0].absolute_path)

        # Ensure it's stereo (if it's not, make it stereo)
        if len(data.shape) == 1:
            data = np.stack((data, data), axis=-1)

        data = trim_to_loop(data, target_samplerate, target_tempo, 4)
        data = fade_out(data, 20, target_samplerate)
        raw_audio_data.append(data)
        target_length = data.shape[0]

        # Resample and read audio files
        for audiofile in audiofile_objects[1:]:
            new_data, new_samplerate = sf.read(audiofile.absolute_path)

            if new_samplerate != target_samplerate:
                resampled_path = resample_audio(audiofile.absolute_path, target_samplerate, f"{audiofile.filename}_resampled.wav")
                new_data, new_samplerate = sf.read(resampled_path)
                audio_paths.append(resampled_path)
            else:
                audio_paths.append(audiofile.absolute_path)

            if len(new_data.shape) == 1:
                new_data = np.stack((new_data, new_data), axis=-1)

            new_data = trim_to_loop(new_data, target_samplerate, target_tempo, 4)
            new_data = fade_out(new_data, 20, target_samplerate)

            if audiofile.instrument_type != "drums" or "percussion":
                new_data = reduce_rms(new_data, -8)
        
            if audiofile.instrument_type == "percussion":
                new_data = reduce_rms(new_data, -10)

            raw_audio_data.append(new_data)

            if new_data.shape[0] > target_length:
                target_length = new_data.shape[0]

        return raw_audio_data, audio_paths, target_samplerate, target_tempo, target_length, key
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def copy_audio_files(audio_paths, new_directory_name):
    output_dir = f"./output/{new_directory_name}"
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Copy each audio file to the output directory
        for path in audio_paths:
            if os.path.exists(path):
                shutil.copy(path, output_dir)
            else:
                print(f"File {path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def fade_out(audio_data, fade_duration_ms, samplerate):
    """
    Apply a linear fade-out to the end of an audio signal.

    Parameters:
    - audio_data: numpy array containing audio data.
    - fade_duration_ms: duration of the fade in milliseconds.
    - samplerate: number of samples per second in the audio data.

    Returns:
    - The audio data with the fade applied.
    """
    
    # Example usage:
    # Assuming 'audio' is a numpy array containing audio data,
    # you want to fade out the last 5000 milliseconds (5 seconds),
    # and your samplerate is 44100 samples per second.
    # audio = fade_out(audio, 5000, 44100)

    # Convert fade duration from milliseconds to seconds
    fade_duration_sec = fade_duration_ms / 1000.0
    
    # Number of samples over which the fade will be applied
    fade_samples = int(fade_duration_sec * samplerate)
    
    # Ensure fade duration is not longer than audio data length
    if fade_samples > audio_data.shape[0]:
        raise ValueError("Fade duration is longer than audio data length.")
    
    # Create a linear fade (1 to 0)
    fade = np.linspace(1, 0, fade_samples)
    
    # If audio data has more than one channel, we need to make the fade array 2D
    if audio_data.ndim > 1:
        fade = fade[:, np.newaxis]

    # Apply the fade to the end of the audio data
    audio_data[-fade_samples:] *= fade
    
    return audio_data

def trim_to_loop(audio_data, sr, tempo, beats_per_measure):
    """
        We first check the number of dimensions of audio_data using ndim. If ndim is 1, the data is mono, and if it is 2, the data is stereo.
    We then perform the trimming or padding operation. For trimming, we simply slice the array up to the loop_end_sample index.
    For padding, we use np.pad. For mono data, we pad only the end of the array. For stereo data, we pad along the first dimension (which represents time) and do not pad the second dimension (which represents channels).
    The mode 'constant' for padding adds zeros (silence) to the audio data.
    This function trims audio data to the nearest fourth measure or pads it up to exactly 4 measures.
    """
    samples_per_beat = int((60.0 / tempo) * sr)
    samples_per_measure = samples_per_beat * beats_per_measure
    four_measures = 4 * samples_per_measure

    # Determine if the audio is mono or stereo
    if audio_data.ndim == 1:
        # Mono audio
        if len(audio_data) >= four_measures:
            # Find the nearest fourth measure to trim to
            num_four_measure_groups = len(audio_data) // four_measures
            nearest_fourth_measure_sample = num_four_measure_groups * four_measures
            audio_data = audio_data[:nearest_fourth_measure_sample]
        else:
            # Pad to exactly 4 measures
            padding_length = four_measures - len(audio_data)
            audio_data = np.pad(audio_data, (0, padding_length), mode='constant')
    else:
        # Stereo audio
        if audio_data.shape[0] >= four_measures:
            # Find the nearest fourth measure to trim to
            num_four_measure_groups = audio_data.shape[0] // four_measures
            nearest_fourth_measure_sample = num_four_measure_groups * four_measures
            audio_data = audio_data[:nearest_fourth_measure_sample, :]
        else:
            # Pad to exactly 4 measures
            padding_length = four_measures - audio_data.shape[0]
            audio_data = np.pad(audio_data, ((0, padding_length), (0, 0)), mode='constant')

    return audio_data

