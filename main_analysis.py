import audio_analysis as analysis
import os
from audiofile import AudioFile
from dbaudiofile import DBAudioFile
from database_setup import Session

directory_path = r"/path/to/your/audio/samples"

def get_audio_filepaths(directory_path, file_extensions=[". wav"]):
    """
    Retrieves all file paths with specified extensions in the given directory and its subdirectories.

    Parameters:
    - directory_path (str): The path to the directory to be searched.
    - file_extensions (list of str, optional): A list of file extensions to be searched for (default is [".wav"]).

    Returns:
    - list of str: The paths to all files with the specified extensions in the directory structure.
    """
    audio_filepaths = []
    
    # Walk through root, dirs, and files in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Check if file ends with one of the desired extensions
            if any(file.lower().endswith(ext) for ext in file_extensions):
                # Construct full path to the audio file and append to list
                audio_filepaths.append(os.path.join(root, file))
    print(f"Total number of audio files found: {len(audio_filepaths)}")
    return audio_filepaths

def create_audio_file_from_analysis(audio_file_path):
    attributes = analysis.analyze(audio_file_path)

    if attributes:
        # Extracting directory and file info
        directory_path, filename = os.path.split(audio_file_path)
        file_name, file_type = os.path.splitext(filename)

        # Instantiate the AudioFile class
        audio_file = AudioFile(
            filename=file_name,
            file_type=file_type.replace('.', ''),  # removing dot from file extension
            absolute_path=audio_file_path,
            directory_path=directory_path,
            key=attributes["musical_key"],
            tempo=attributes["tempo"],
            instrument_type=attributes["instrument_type"],
            length_in_samples=attributes["length_in_samples"],
            sample_rate=attributes["sample_rate"],
        )
        return audio_file

def create_db_audiofile(audio_file):
    """
    Converts an AudioFile object into a DBAudioFile object.
    
    Parameters:
        audio_file (AudioFile): The AudioFile object to convert.
    
    Returns:
        DBAudioFile: A corresponding DBAudioFile object.
    """
    return DBAudioFile(
        filename=audio_file.filename,
        file_type=audio_file.file_type,
        absolute_path=audio_file.absolute_path,
        directory_path=audio_file.directory_path,
        key=audio_file.key,
        genre=audio_file.genre,
        scale_mode=audio_file.scale_mode,
        tempo=audio_file.tempo,
        instrument_type=audio_file.instrument_type,
        length_in_samples=audio_file.length_in_samples,
        sample_rate=audio_file.sample_rate,
    )

def commit_audio_files_to_db(audio_files):
    session = Session()

    try:
        for audio_file in audio_files:
            my_db_audiofile = create_db_audiofile(audio_file)
            session.add(my_db_audiofile)
        session.commit()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        session.rollback()
    finally:
        session.close()

audio_files_buffer = []
BUFFER_SIZE = 100  # The number of files to commit at a time

file_extensions = [".wav"]  # Add or remove desired audio file extensions
audio_paths = get_audio_filepaths(directory_path, file_extensions)

remaining_files = len(audio_paths)

for path in audio_paths:
    audio_file = create_audio_file_from_analysis(path)
    remaining_files = remaining_files - 1
    if audio_file is not None:
        audio_files_buffer.append(audio_file)

    print(f"Files remaining: {remaining_files}")

    if len(audio_files_buffer) >= BUFFER_SIZE:
        commit_audio_files_to_db(audio_files_buffer)
        audio_files_buffer.clear()

# Don't forget to commit the last batch if there are any left
if audio_files_buffer:
    commit_audio_files_to_db(audio_files_buffer)
