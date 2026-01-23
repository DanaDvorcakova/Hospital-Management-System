import os

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL","sqlite:///hospital.db")





