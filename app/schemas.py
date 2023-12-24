
from datetime import datetime
from pydantic import BaseModel, EmailStr, conint
from typing import Optional


class PostBase(BaseModel): 
    title: str
    content: str 
    
    published:bool  = True

class CreatePost(PostBase):
    pass

class UserOut(BaseModel):
    id:int
    email: EmailStr
    created_at: datetime   
    class Config:
        from_attributes = True

class Post(PostBase):
    id:int
    created_at: datetime
    owner_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post:Post
    votes:int

    class Config:
        from_attributes = True


class CreateUser(BaseModel):
    email: EmailStr
    password: str

class UserCredentials(BaseModel): 
    email:str 
    password: str

class Token(BaseModel):
    token:str
    type:str

class TokenData(BaseModel):
    id:Optional[int] =None

    class Config:
        from_attribute = True


class CreateVote(BaseModel):
    post_id:int 
    dir: conint(le=1)