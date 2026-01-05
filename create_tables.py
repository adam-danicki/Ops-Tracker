from app.db import engine, Base
from app.models.project import Project

def create_tables():
    # Create all tables in the database
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()


