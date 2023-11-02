import audio_analysis as analysis 
from audiofile import AudioFile
from dbaudiofile import DBAudioFile
from database_setup import Session
from sqlalchemy import func

def get_random_audio_file():
    session = Session()
    try:
        # Order the results randomly and return the first
        random_audio_file = session.query(DBAudioFile).filter_by(instrument_type="Drums").order_by(func.random()).first()
        return random_audio_file
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    finally:
        session.close()

def get_total_audio_files_count():
    """
    Retrieve the total number of audio files in the database.

    Returns:
    - int: The total number of DBAudioFile instances in the database.
    """
    session = Session()
    try:
        # Query the database to count all DBAudioFile entries
        total_count = session.query(DBAudioFile).count()
        return total_count
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0
    finally:
        session.close()


def get_audiofile_by_instrument_tempo_key(attribute_dict):
    """
    Retrieve a DBAudioFile with a specified instrument_type, within a specified tempo range, and within a specified key range.

    Parameters:
    Parameters:
    - attribute_dict (dict): A dictionary containing 'instrument_type', 'tempo_min', 'tempo_max', 'key_rang'.

    Returns:
    - DBAudioFile: The retrieved DBAudioFile instance, or None if no matching instance was found.
    
    Example dictionary:
    attributes = {
        "instrument_type": "melodic",
        "tempo_min": 70,
        "tempo_max": 120,
        "key_range": ["A","B","C"]
    }
    """
    session = Session()
    try:
        # Query the database for a DBAudioFile with the specified instrument_type, tempo range, and key range
        audio_file = (
            session.query(DBAudioFile)
            .filter_by(instrument_type=attribute_dict["instrument_type"])
            .filter(DBAudioFile.tempo.between(attribute_dict["tempo_min"], attribute_dict["tempo_max"]))
            .filter(DBAudioFile.key.in_(attribute_dict["key_range"]))
            .order_by(func.random())
            .first()
        )
        return audio_file
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    finally:
        session.close()

def fetch_and_print_all_audiofiles():
    """
    Retrieve all DBAudioFile objects and print their attributes in a human-readable format.
    """
    session = Session()
    try:
        # Query the database for all DBAudioFile entries
        audio_files = session.query(DBAudioFile).all()
        
        if not audio_files:
            print("No audio files found in the database.")
            return
        
        for audio_file in audio_files:
            print("-" * 50)  # separator for clarity
            print(f"Filename: {audio_file.filename}")
            print(f"File Type: {audio_file.file_type}")
            print(f"Absolute Path: {audio_file.absolute_path}")
            print(f"Directory Path: {audio_file.directory_path}")
            print(f"Key: {audio_file.key}")
            print(f"Tempo: {audio_file.tempo}")
            print(f"Instrument Type: {audio_file.instrument_type}")
            print(f"Length in Samples: {audio_file.length_in_samples}")
            print(f"Sample Rate: {audio_file.sample_rate}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()

def count_audiofiles_by_instrument_type():
    """
    Count and print the number of audio files for each instrument type.
    """
    session = Session()
    try:
        instrument_types = ["drums", "bass", "melodic", "fx", "vocals", "percussion","undetermined"]

        for instrument_type in instrument_types:
            count = session.query(DBAudioFile).filter_by(instrument_type=instrument_type).count()
            print(f"Number of audio files with instrument type '{instrument_type}': {count}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()

def count_audiofiles_by_key():
    """
    Count and print the number of audio files for each musical key.
    """
    session = Session()
    try:
        # Query for distinct keys in the database
        distinct_keys = session.query(DBAudioFile.key).distinct().all()

        for key in distinct_keys:
            key_name = key[0]  # Extract the key name from the tuple
            count = session.query(DBAudioFile).filter_by(key=key_name).count()
            print(f"Number of audio files in key '{key_name}': {count}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        session.close()