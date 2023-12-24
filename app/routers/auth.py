
from fastapi import APIRouter, Depends, Body, HTTPException, status

from sqlalchemy.orm import Session

from .. import database
from .. import schemas, models, utils, oauth2

from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Auth"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials :OAuth2PasswordRequestForm = Depends(),db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user: 
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    
    return {"token": access_token, "type": "bearer"}