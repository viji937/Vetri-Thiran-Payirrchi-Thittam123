from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(50))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_user(data: dict) -> User:
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.user_id == data["user_id"]))
        if existing:
            existing.username = data["username"]
            existing.age = data["age"]
            existing.weight = data["weight"]
            existing.goal = data["goal"]
            existing.intensity = data["intensity"]
            db.commit()
            db.refresh(existing)
            return existing

        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def save_plan(user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    with SessionLocal() as db:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


def get_user(user_id: str) -> Optional[User]:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.user_id == user_id))


def get_latest_plan(user_id: str) -> Optional[Plan]:
    with SessionLocal() as db:
        stmt = (
            select(Plan)
            .where(Plan.user_id == user_id)
            .order_by(Plan.id.desc())
        )
        return db.scalar(stmt)


def update_plan(
    user_id: str,
    updated_plan: str,
    feedback: str,
) -> Optional[Plan]:
    with SessionLocal() as db:
        stmt = (
            select(Plan)
            .where(Plan.user_id == user_id)
            .order_by(Plan.id.desc())
        )
        plan = db.scalar(stmt)
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.feedback = feedback
        db.commit()
        db.refresh(plan)
        return plan


def get_all_users() -> list[User]:
    with SessionLocal() as db:
        return list(db.scalars(select(User).order_by(User.id.desc())).all())


def get_all_plans() -> list[Plan]:
    with SessionLocal() as db:
        return list(db.scalars(select(Plan).order_by(Plan.id.desc())).all())


def delete_user(user_id: str) -> bool:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return False
        plans = list(db.scalars(select(Plan).where(Plan.user_id == user_id)).all())
        for plan in plans:
            db.delete(plan)
        db.delete(user)
        db.commit()
        return True
