from typing import Union
from fastapi import UploadFile
from models import ArtifactTypeEnum

from pydantic import BaseModel


class ArtifactBase(BaseModel):
    name: str
    version: int
    type: ArtifactTypeEnum
    path: Union[str, None] = None

class ArtifactCreate(ArtifactBase):
    file: UploadFile

class Artifact(ArtifactBase):

    class Config:
        orm_mode = True

