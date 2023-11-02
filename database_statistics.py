import read_database

total_count = read_database.get_total_audio_files_count()
print(f"There are {total_count} audio files in the database.")

read_database.count_audiofiles_by_key()
read_database.count_audiofiles_by_instrument_type()