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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# to get a string like this run:
# openssl rand -hex 32
try:
    SECRET_KEY = os.environ[
        "SECRET_KEY"
    ]  
except KeyError:
    from subprocess import run
    SECRET_KEY = (
        run("openssl rand -hex 32", capture_output=True, shell=True, check=False)
        .stdout.decode("utf-8")
        .strip()
    )
ALGORITHM = "HS256"
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
except KeyError:
    ACCESS_TOKEN_EXPIRE_MINUTES = -1


# hash the password with bcrypt

hashed_password = pwd_context.hash(os.environ["PASSWORD"])
os.environ.pop("PASSWORD")
env_users_db = {
    os.environ["USER"]: {
        "username": os.environ["USER"],
        "hashed_password": hashed_password,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str


app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
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

    user = get_user(env_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(env_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if ACCESS_TOKEN_EXPIRE_MINUTES == "-1":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        access_token_expires = None
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# API functionnalities
@app.get("/api/v1/exists")
async def file_exists(
    token: Annotated[str, Depends(oauth2_scheme)], path: Optional[str] = None
) -> dict:
    """Check if a file exists in the vault

    Args:
        path (Optional[str], optional): Path to the file. Defaults to None.

    Returns:
        dict: A json object notifying if the file exists or not under the "file exists" key
    """

    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        return {"file exists": True}
    else:
        return {"file exists": False}


class append_Model(BaseModel):
    """Model used to append text to a file in the vault. It is comprised of the path to the file and the text to add 
    """
    path: str
    text: str


@app.post("/api/v1/append")
def append_to_file(
    _: Annotated[str, Depends(oauth2_scheme)], item: append_Model
) -> dict:
    """Add text to a file in the vault

    Args:
        _ (Annotated[str, Depends): authentication token
        item (append_Model): item comprised of the path to the file and the text to add

    Raises:
        HTTPException: Code 400 if the path is not provided

    Returns:
        dict: A json object recaping the action performed under the "action" key
    """    

    if item.path is None:
        raise HTTPException(status_code=400, detail="Path not provided")

    vault_path = os.getenv("VAULT_PATH")
    with open(os.path.join(vault_path, item.path), "a") as f:
        f.write("\n" + item.text)
    return {"action": f"added {item.text} to {item.path}"}


@app.get("/api/v1/content")
async def file_content(
    _: Annotated[str, Depends(oauth2_scheme)], path: Optional[str] = None
) -> dict:
    """Retruns the content of a file in the vault

    Args:
        _ (Annotated[str, Depends): authentication token
        path (Optional[str], optional): relative path of a file in the vault. Defaults to None.

    Raises:
        HTTPException: Code 400 if the path is not provided
        HTTPException: Code 400 if the file does not exist

    Returns:
        dict: A json object containing the content of the file under the "content" key
    """    
    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        with open(os.path.join(vault_path, path), "r") as f:
            return {"content": f.read()}
    else:
        raise HTTPException(status_code=400, detail="File does not exist")


@app.get("/api/v1/metadata")
async def file_metadata(
    _: Annotated[str, Depends(oauth2_scheme)], path: Optional[str] = None
) -> dict:
    """Retruns the obsidian file properties

    Args:
        _ (Annotated[str, Depends): authentication token
        path (Optional[str], optional): relative path of a file in the vault. Defaults to None.

    Raises:
        HTTPException: Code 400 if the path is not provided
        HTTPException: Code 400 if the file does not exist

    Returns:
        dict: A json object containing the properties of the file under the "metadata" key
    """
    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        with open(os.path.join(vault_path, path), "r") as f:
            # read the file and if the file contains a yaml header contained between --- and --- return the yaml header
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

            # else return an empty dict
        metadata = yaml.safe_load(metadata)
        if metadata is None:
            metadata = {}
        return {"metadata": metadata}
    else:
        raise HTTPException(status_code=400, detail="File does not exist")
