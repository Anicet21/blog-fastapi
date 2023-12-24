from typing import List, Optional
from fastapi import Depends, Path,Body, HTTPException, status, Response, APIRouter, Query

from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import schemas, models,oauth2

from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags= ["Posts"]
)
#@router.get('/', response_model=List[schemas.PostOut])
@router.get('/', response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),limit:int =5, skip:int =0, q : Optional[str] = ""):
    # cursor.execute(""" SELECT * FROM posts """) 
    #posts = cursor.fetchall()
    #posts = db.query(models.Post,).filter(models.Post.title.contains(q)).limit(limit).offset(skip).all()
    posts= db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(q)).limit(limit).offset(skip).all()
    #result = [{"Post": post[0].__dict__, "votes": post[1]} for post in postvote]

    #print(result)
    return posts

@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id:int = Path(...),db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id))) 
    # post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= f"Post with id {id} was not found"
        )
    return  post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int = Path(...),db: Session = Depends(get_db), current_user: schemas.TokenData  = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id))) 
    # post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= f"Post with id {id} was not found"
        )
    
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail= "Unauthorized We could not perform the action."
        )


    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int = Path(...),payload: schemas.CreatePost = Body(...),db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
  
    # cursor.execute(""" UPDATE posts set title = %s, content = %s, published = %s  where id = %s RETURNING *""", (payload.title, payload.content, payload.published, str(id)))
    # update_post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id)
    update_post = post.first()
    if update_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= f"Post with id {id} was not found"
        )
    
    if update_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail= "Unauthorized We could not perform the action."
        )
    
    post.update(payload.dict(), synchronize_session=False)
    db.commit()

    return  post.first()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(payload:  schemas.CreatePost = Body(...),db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (payload.title, payload.content, payload.published))
    # new_post = cursor.fetchone() 
    # conn.commit() 
   # print(f"******************** {current_user} ******************")
    new_post =models.Post(owner_id= current_user.id, **payload.model_dump())    
    db.add(new_post) 
    db.commit()
    db.refresh(new_post) 
    return  new_post

