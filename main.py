from typing import Optional
import os 
from fastapi import FastAPI
app = FastAPI()

##
@app.get("/exists")
async def fileExists(path: Optional[str] = None) -> dict:
    """Check if a file exists

    Args:
        path (Optional[str], optional): Path to the file. Defaults to None.

    Returns:
        dict: _description_
    """

    vault_path = os.getenv("VAULT_PATH")

    if os.path.exists(os.path.join(vault_path, path)):
        return {"file exists": True}
    else:
        return {"file exists": False}


