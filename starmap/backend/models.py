from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id           = Column(Integer, primary_key=True, index=True)
    email        = Column(String(120), unique=True, index=True, nullable=False)
    username     = Column(String(50), nullable=False)
    avatar       = Column(Text, default="")
    bio          = Column(String(200), default="")
    lang         = Column(String(10), default="zh")
    hashed_pw    = Column(String(255), nullable=False)
    is_active    = Column(Boolean, default=True)
    photo_tags   = Column(Text, default="{}")   # JSON: {"星空":3,"城市":1,...}
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    saved_points = relationship("SavedPoint", back_populates="user", cascade="all, delete")
    photos       = relationship("UserPhoto", back_populates="user", cascade="all, delete")

class EmailCode(Base):
    __tablename__ = "email_codes"
    id         = Column(Integer, primary_key=True)
    email      = Column(String(120), index=True, nullable=False)
    code       = Column(String(6), nullable=False)
    purpose    = Column(String(20), default="register")
    used       = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedPoint(Base):
    __tablename__ = "saved_points"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    name       = Column(String(200), nullable=False)
    lat        = Column(Float, nullable=False)
    lng        = Column(Float, nullable=False)
    note       = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User", back_populates="saved_points")

class UserPhoto(Base):
    __tablename__ = "user_photos"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    tags       = Column(Text, default="[]")   # JSON list of detected tags
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User", back_populates="photos")


class CommunityPhoto(Base):
    __tablename__ = "community_photos"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_name  = Column(String(200), nullable=False, index=True)
    lat        = Column(Float, nullable=False)
    lng        = Column(Float, nullable=False)
    image_data = Column(Text, nullable=False)       # base64 data URI
    caption    = Column(String(300), default="")
    likes      = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User")


class PhotoLike(Base):
    __tablename__ = "photo_likes"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_id   = Column(Integer, ForeignKey("community_photos.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PhotoSave(Base):
    __tablename__ = "photo_saves"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_id   = Column(Integer, ForeignKey("community_photos.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PhotoComment(Base):
    __tablename__ = "photo_comments"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_id   = Column(Integer, ForeignKey("community_photos.id"), nullable=False)
    content    = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User")


class SpotRating(Base):
    __tablename__ = "spot_ratings"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    spot_name  = Column(String(200), nullable=False, index=True)
    score      = Column(Integer, nullable=False)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User")
