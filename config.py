import os

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://hospital_db_v57t_user:6mYkKVljqO8kxDqPWTOmxWgT2p72TCJ2@dpg-d5pukpf5r7bs738m9oj0-a.frankfurt-postgres.render.com/hospital_db_v57t")

#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL","sqlite:///hospital.db")




