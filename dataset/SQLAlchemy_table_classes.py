from sqlalchemy import Column, Integer, String, JSON, CheckConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Image(Base):
    __tablename__ = 'image'

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(256), nullable=False)

    # Relationship to Label
    labels = relationship("Label", back_populates="image")

    def __repr__(self):
        return f"{self.id}, {self.path}"


class Label(Base):
    __tablename__ = 'label'

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey('image.id'), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    misc = Column(JSON, nullable=True)

    # Relationship to Image
    image = relationship("Image", back_populates="labels")

    # Constraints
    __table_args__ = (
        CheckConstraint('x >= 0 AND x < 65536', name='check_x_range'),
        CheckConstraint('y >= 0 AND y < 65536', name='check_y_range'),
        CheckConstraint('width >= 0 AND width < 65536 AND x + width < 65536', name='check_width_range'),
        CheckConstraint('height >= 0 AND height < 65536 AND y + height < 65536', name='check_height_range'),
    )

    def __repr__(self):
        return f"{self.id}, {self.image_id}"
