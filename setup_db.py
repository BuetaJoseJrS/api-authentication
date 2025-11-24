from database import SessionLocal, engine, Base
import crud

# 1. Create all tables in the database
Base.metadata.create_all(bind=engine)

def init_db():
    db = SessionLocal()
    
    # 2. Create roles if they don't exist
    if not crud.get_role_by_name(db, "user"):
        crud.create_role(db, "user", "Regular user")
        print("Created role: user")
        
    if not crud.get_role_by_name(db, "admin"):
        crud.create_role(db, "admin", "Administrator")
        print("Created role: admin")
        
    if not crud.get_role_by_name(db, "moderator"):
        crud.create_role(db, "moderator", "Moderator")
        print("Created role: moderator")

    db.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()