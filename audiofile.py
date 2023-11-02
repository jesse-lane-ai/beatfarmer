class AudioFile:
    FILE_TYPES = ["wav"]
    MUSICAL_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    SCALE_MODES = ["Major", "Minor", "Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]
    
    @property
    def tempo(self):
        return self._tempo
    
    @tempo.setter
    def tempo(self, new_tempo):
        self._tempo = self._validate_number(new_tempo, minimum=0, default=None)
        
    @property
    def length_in_samples(self):
        return self._length_in_samples
    
    @length_in_samples.setter
    def length_in_samples(self, new_length):
        self._length_in_samples = self._validate_number(new_length, minimum=0, default=None)

    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, new_sample_rate):
        self._sample_rate = self._validate_number(new_sample_rate, minimum=0, default=None)

    @property
    def key(self):
        return self._key
    
    @key.setter
    def key(self, new_key):
        self._key = self._validate_enum(new_key, self.MUSICAL_KEYS, default="undetermined")

    @property
    def scale_mode(self):
        return self._scale_mode
    
    @scale_mode.setter
    def scale_mode(self, new_scale_mode):
        self._scale_mode = self._validate_enum(new_scale_mode, self.SCALE_MODES, default="undetermined")

    @property
    def file_type(self):
        return self._file_type
    
    @file_type.setter
    def file_type(self, new_file_type):
        self._file_type = self._validate_enum(new_file_type, self.FILE_TYPES)

    def __init__(self, filename, file_type, absolute_path, directory_path, 
                 key="undetermined", scale_mode="undetermined", 
                 tempo=None, genre="undetermined", 
                 instrument_type="undetermined", 
                 length_in_samples=None, sample_rate=None):
        self.filename = filename
        self.file_type = file_type
        self.absolute_path = absolute_path
        self.directory_path = directory_path
        self.key = key
        self.scale_mode = scale_mode
        self.tempo = tempo
        self.genre = genre
        self.instrument_type = instrument_type
        self.length_in_samples = length_in_samples
        self.sample_rate = sample_rate
    
    @staticmethod
    def _validate_enum(value, valid_options, default=None):
        """
        Validates if the value is among the valid options.
        
        :param value: The value to validate.
        :param valid_options: A list of valid options.
        :param default: The default value to return if validation fails.
        :raises ValueError: If value is not valid and no default is provided.
        :return: The validated value or default.
        """
        if value not in valid_options:
            if default is not None:
                return default
            raise ValueError(f"Invalid value: {value}. Expected one of: {', '.join(valid_options)}.")
        return value

    @staticmethod
    def _validate_number(value, minimum=None, default=None):
        """
        Validates if the value is a number and meets the minimum requirement.
        
        :param value: The value to validate.
        :param minimum: The minimum acceptable value.
        :param default: The default value to return if the value is None.
        :raises TypeError: If value is not a number.
        :raises ValueError: If value is less than the minimum.
        :return: The validated number or default.
        """
        if value is not None:
            if not isinstance(value, (int, float)):
                raise TypeError(f"Invalid type: {type(value)}. Raw data: {value}. Expected int or float.")
            if minimum is not None and value < minimum:
                raise ValueError(f"Invalid value: {value}. Expected a number >= {minimum}.")
        else:
            return default
        return value

    def __str__(self):
        """
        Returns a string representation of the AudioFile object.

        :return: A string representation of the object.
        """
        return f"AudioFile({self.filename}, {self.file_type}, instrument= {self.instrument_type} key={self.key}, scale_mode={self.scale_mode}, tempo={self.tempo})"