from auth import get_current_user
from cfg import app
from fastapi import Depends, HTTPException, status
from model import Comment, Post, User
from cfg import get_db_session
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session


class CreateCommentRequest(BaseModel):
    body: str


class CreatePostRequest(BaseModel):
    title: str
    body: str


class UserInfo(BaseModel):
    id: int
    username: str


@app.get("/me", response_model=UserInfo)
async def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


@app.post("/posts")
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    post = Post(title=request.title, body=request.body, user_id=current_user.id)
    db_session.add(post)
    db_session.flush()
    db_session.refresh(post)

    return post


@app.get("/posts")
async def get_posts(
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    return db_session.execute(select(Post)).scalars().all()


@app.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    post = db_session.execute(
        select(Post).where(Post.id == post_id)
    ).scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No post found"
        )
    comment = Comment(body=request.body, author=current_user, post_id=post_id)

    db_session.add(comment)
    db_session.flush()
    db_session.refresh(comment)

    return comment


@app.get("/posts/{post_id}/comments")
def get_comments(
    post_id,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session),
):
    post = db_session.execute(
        select(Post).where(Post.id == post_id)
    ).scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No post found"
        )

    comments = (
        db_session.execute(select(Comment).where(Comment.post_id == post_id))
        .scalars()
        .all()
    )

    return comments
