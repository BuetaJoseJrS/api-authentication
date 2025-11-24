from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Import from our new database modules
from database import get_db
import crud
from auth import (
    create_access_token, 
    get_current_active_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
# authenticate_user is now in crud.py, but we can call it directly or import via auth if wrapper exists.
# To match your previous crud.py structure, we will use crud.authenticate_user directly.

from models import User, UserCreate 

app = FastAPI(title="JWT Authentication Demo", version="1.0.0")


# --- 1. Registration Endpoint (REAL DATABASE) ---
@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user to the REAL SQLite database.
    """
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user_email = crud.get_user_by_email(db, email=user_data.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create the user in the database
    return crud.create_user(db=db, user=user_data)


# --- 2. Login Endpoint (REAL DATABASE) ---
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # We use the authenticate_user function from crud.py
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- 3. Protected Endpoints ---
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.full_name}, this is a protected route!"}