from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Video(Base):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False)

    frame = relationship("Frame", back_populates="video")


class Frame(Base):
    __tablename__ = 'frame'
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey('video.id', ondelete='CASCADE'), nullable=False)
    frame_num = Column(Integer, nullable=False)

    video = relationship("Video", back_populates="frame")
    label = relationship("Label", back_populates="frame")


class Label(Base):
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True, autoincrement=True)
    frame_id = Column(Integer, ForeignKey('frame.id', ondelete='CASCADE'), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    misc = Column(JSON, nullable=True)

    frame = relationship("Frame", back_populates="label")
