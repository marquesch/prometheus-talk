import random
from typing import List

from cfg import Base, engine, Session
from sqlalchemy import ForeignKey, String, Text, select
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_plaintext: Mapped[str] = mapped_column(String(100))

    posts: Mapped[List["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"

    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username}


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    body: Mapped[str] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, user_id={self.user_id!r})"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="comments")

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment(id={self.id!r}, post_id={self.post_id!r}, user_id={self.user_id!r})"


Base.metadata.create_all(bind=engine)


def seed_database():
    """Seeds the database with test data if it's empty."""

    user_data = [
        ("reader_user", "reader_pass"),
        ("contributor_user", "contributor_pass"),
        ("power_user", "power_pass"),
    ]

    post_titles = [
        "Getting Started with FastAPI",
        "Understanding Docker Compose",
        "Prometheus Metrics Best Practices",
        "Grafana Dashboard Design Tips",
        "Load Testing with Locust",
        "Building RESTful APIs",
        "Database Optimization Techniques",
        "Monitoring Production Systems",
        "Microservices Architecture",
        "CI/CD Pipeline Setup",
        "Python Performance Tips",
        "Web Security Essentials",
        "Scaling Web Applications",
        "Container Orchestration",
        "API Rate Limiting Strategies",
        "Debugging Distributed Systems",
        "Cloud Infrastructure Basics",
        "DevOps Best Practices",
        "Logging and Tracing",
        "Authentication Patterns",
    ]

    comment_templates = [
        "Great article! Thanks for sharing.",
        "This is very helpful information.",
        "I have a question about this approach.",
        "Excellent explanation!",
        "Could you provide more details?",
        "This solved my problem, thank you!",
        "Interesting perspective on this topic.",
        "I disagree with some points here.",
        "Looking forward to more content like this.",
        "Well written and informative.",
    ]

    with Session() as session:
        existing_user = session.execute(
            select(User).where(User.username == user_data[0][0])
        ).scalar_one_or_none()

        if existing_user is not None:
            return

        users = []
        for username, password in user_data:
            user = User(username=username, password_plaintext=password)
            users.append(user)
            session.add(user)
        session.flush()

        posts = []
        for i, title in enumerate(post_titles, 1):
            user = random.choice(users)
            post = Post(
                title=title,
                body=f"Content for {title.lower()}. ID: {i}",
                user_id=user.id,
            )
            posts.append(post)
            session.add(post)
        session.flush()

        comments = []
        for post in posts:
            num_comments = random.randint(2, 5)
            for _ in range(num_comments):
                user = random.choice(users)
                comment = Comment(
                    body=random.choice(comment_templates),
                    user_id=user.id,
                    post_id=post.id,
                )
                comments.append(comment)
                session.add(comment)

        session.commit()


seed_database()
