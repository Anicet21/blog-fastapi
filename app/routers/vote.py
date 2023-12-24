

from fastapi import Depends, Path,Body, HTTPException, status, Response, APIRouter

from .. import models, oauth2, database, schemas

from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.CreateVote = Body(...),  db: Session = Depends(database.get_db),  current_user: schemas.TokenData  = Depends(oauth2.get_current_user) ): 
    
   founded_post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

   if not founded_post:
      raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"The post {vote.post_id} does not exist"
         )

   vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id )
   founded_vote = vote_query.first()
   if vote.dir == 1:
      if founded_vote:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"You've already vote this post"
         )
      
      vote_data = models.Vote(user_id=current_user.id, post_id=vote.post_id)

      db.add(vote_data)
      db.commit()

      return {"message": "Vote has been added successfully"}

   else:
      if not founded_vote:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= "Vote does not existe"
         )
      vote_query.delete(synchronize_session=False)
      db.commit()
      return {"message": "Vote has been deleted successfully"}