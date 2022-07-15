import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


association_table = Table(
    "association",
    Base.metadata,
    Column("artifact_id", ForeignKey("artifacts.id"), primary_key=True),
    Column("handler_id", ForeignKey("handlers.id"), primary_key=True),
)

class ArtifactTypeEnum(enum.Enum):
    model = "model"
    code = "code"

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), index=True)
    version = Column(Integer, nullable=False, default=0)
    path = Column(String(256), nullable=False)
    type = Column(Enum(ArtifactTypeEnum), nullable=False, default="model")


class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True)
    handlers = relationship("Handler", back_populates="endpoint")

class Handler(Base):
    __tablename__ = "handlers"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, nullable=False, default=0)
    name = Column(String(256), index=True)
    docker_image = Column(String(256), nullable=False)
    prod_traffic = Column(Integer, nullable=False, default=0)
    shadow_traffic = Column(Integer, nullable=False, default=0)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    endpoint = relationship("Endpoint", back_populates="handlers")
    UniqueConstraint(endpoint_id, name, name='endpoint_handler')
    artifacts = relationship("Artifact", secondary=association_table)

 


