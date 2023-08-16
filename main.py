from typing import Optional
import os 
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/exists")
async def file_exists(path: Optional[str] = None) -> dict:
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
def append_to_file(item: append_Model) -> dict:
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
async def file_content(path: Optional[str] = None) -> dict:

    if path is None:
        raise HTTPException(status_code=400, detail="Path not provided")
    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        with open(os.path.join(vault_path, path), "r") as f:
            return {"content": f.read()}
    else:
        raise HTTPException(status_code=400, detail="File does not exist")


@app.get("/metadata")
async def file_metadata(path: Optional[str] = None) -> dict:

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
