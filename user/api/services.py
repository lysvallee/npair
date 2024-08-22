from sqlmodel import Session, create_engine, SQLModel

DATABASE_URL="postgresql://admin:3Dgen_gltf@db/npair_db"

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Create a database session.
def get_db():
    with Session(engine) as session:
        yield session
    
