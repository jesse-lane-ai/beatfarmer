# database_setup.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbaudiofile import Base  # Import the Base from models.py

DATABASE_URL = "sqlite:///audiofile.db"  # Use your actual DB URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Ensure tables are created

Session = sessionmaker(bind=engine)
