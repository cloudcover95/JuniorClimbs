from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "coach" or credentials.password != "juniorclimbs2026":
        raise HTTPException(401, "Invalid coach credentials")
    return credentials.username
