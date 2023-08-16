from datetime import datetime, timedelta
from typing import Optional, Annotated
import os 
import yaml
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()


# Authentication
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ["SECRET_KEY"]#"6a247d8d0aacc1ccab599576e8208acd250cbe2cfdb8a3f8900c0d7e853c2c06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}




# API functionnalities
    
@app.get("/exists")
async def file_exists( user: Annotated[User, Depends(get_current_active_user)], path: Optional[str] = None) -> dict:
    """Check if a file exists

    Args:
        path (Optional[str], optional): Path to the file. Defaults to None.

    Returns:
        dict: _description_
    """

    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        return {"file exists": True}
    else:
        return {"file exists": False}

class append_Model(BaseModel):
    path : str
    text: str

@app.post("/append")
def append_to_file(user: Annotated[User, Depends(get_current_active_user)], item: append_Model) -> dict:
    """
    Append to a file (create if not exists) located in a path
    """

    if item.path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    
    vault_path = os.getenv("VAULT_PATH")
    with open(os.path.join(vault_path, item.path), "a") as f:
        f.write("\n"+item.text)
    return {"action": f"added {item.text} to {item.path}"}


@app.get("/content")
async def file_content(user: Annotated[User, Depends(get_current_active_user)], path: Optional[str] = None) -> dict:

    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        with open(os.path.join(vault_path, path), "r") as f:
            return {"content": f.read()}
    else:
        raise HTTPException(status_code=400, detail="File does not exist")


@app.get("/metadata")
async def file_metadata(user: Annotated[User, Depends(get_current_active_user)], path: Optional[str] = None) -> dict:

    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        with open(os.path.join(vault_path, path), "r") as f:
            #read the file and if the file contains a yaml header contained between --- and --- return the yaml header
            file_content = f.readlines()
            metadata = ""
            reading_metadata = False
            for line in file_content[1:]:
                if reading_metadata and line[0:3] == "---":
                    break
                elif reading_metadata and line != "---\n":
                    metadata += line
                
                if line == "":
                    pass
                elif line != "---\n" and line != "\n":
                    pass
                elif line == "---\n":
                    reading_metadata = True


            #else return an empty dict
        metadata = yaml.safe_load(metadata)
        if metadata is None:
            metadata = {}
        return {"metadata": metadata}
    else:
        raise HTTPException(status_code=400, detail="File does not exist")
