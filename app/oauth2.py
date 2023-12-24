
from jose import JWTError, jwt
from datetime import datetime, timedelta

from fastapi import HTTPException , status , Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from . import schemas, database, models, config

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.access_token_expire_minuites

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp":expire
    })

    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token


def verifiy_access_token(token:str, credential_exceptions):

    try:
       payload = jwt.decode(token=token,key= SECRET_KEY,  algorithms=[ALGORITHM])
       id: int = payload.get("user_id")
       if id is None:
           raise credential_exceptions
       #print(f"peut etre icicic {id}")
       token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credential_exceptions
    
    return token_data



def get_current_user(token:str = Depends(oauth2_scheme), db : Session = Depends(database.get_db)): 
    credential_exceptions =  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f"INVALID TOKEN", 
        headers={"WWW-AUTHENTICATE":"Bearer"}
    )

    token_user = verifiy_access_token(token,credential_exceptions)

    user = db.query(models.User).filter(models.User.id == token_user.id).first()

    return user
