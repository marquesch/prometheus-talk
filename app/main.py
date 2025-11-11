from auth import get_current_user
from cfg import Session, app
from fastapi import Depends, HTTPException, status
from model import Comment, Post, User
from pydantic import BaseModel
from sqlalchemy import select


class CreateCommentRequest(BaseModel):
    body: str


class CreatePostRequest(BaseModel):
    title: str
    body: str


class UserInfo(BaseModel):
    id: int
    username: str


@app.get("/health")
async def health_check():
    return "ok"


@app.get("/me", response_model=UserInfo)
async def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


@app.post("/posts")
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
):
    post = Post(title=request.title, body=request.body, user_id=current_user.id)
    with Session() as session:
        session.add(post)
        session.commit()
        session.refresh(post)

        return post


@app.get("/posts")
async def get_posts(
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        return session.execute(select(Post)).scalars().all()


@app.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        post = session.execute(
            select(Post).where(Post.id == post_id)
        ).scalar_one_or_none()

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No post found"
            )
        comment = Comment(body=request.body, author=current_user, post_id=post_id)

        session.add(comment)
        session.commit()
        session.refresh(comment)

        return comment


@app.get("/posts/{post_id}/comments")
def get_comments(
    post_id,
    current_user: User = Depends(get_current_user),
):
    with Session() as session:
        post = session.execute(
            select(Post).where(Post.id == post_id)
        ).scalar_one_or_none()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No post found"
            )

        comments = (
            session.execute(select(Comment).where(Comment.post_id == post_id))
            .scalars()
            .all()
        )

        return comments
