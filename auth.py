from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Import your new database files
from database import get_db, DBUser
import crud  # This allows us to use get_user_by_username
from models import User

# --- Configuration ---
SECRET_KEY = "your-secret-key-here"  # CHANGE THIS IN PRODUCTION
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Helper Function: Convert DB User to Pydantic Model ---
def convert_db_user_to_user(db_user: DBUser) -> User:
    """Convert database user object to Pydantic user model."""
    if not db_user:
        return None
    
    # Get role names from the relationship
    role_names = [role.name for role in db_user.roles]
    
    return User(
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        disabled=not db_user.is_active, # Map is_active to disabled
        roles=role_names # Add roles to the model
    )

# --- Token Creation ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Authentication Dependencies ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the JWT token using the database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Use CRUD to get the user from the REAL database
    db_user = crud.get_user_by_username(db, username=username)
    
    if db_user is None:
        raise credentials_exception
        
    # Convert the DB object to a format main.py understands
    return convert_db_user_to_user(db_user)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Check if the user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user