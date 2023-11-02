from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DBAudioFile(Base):
    __tablename__ = 'audiofiles'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_type = Column(String)
    absolute_path = Column(String)
    directory_path = Column(String)
    key = Column(String)
    tempo = Column(Float)
    scale_mode = Column(String)
    genre = Column(String)
    instrument_type = Column(String)
    length_in_samples = Column(Integer)
    sample_rate = Column(Integer)
