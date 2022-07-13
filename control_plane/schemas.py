from fastapi import UploadFile
from .models import ArtifactTypeEnum

from pydantic import BaseModel


class ArtifactBase(BaseModel):
    name: str
    version: int
    type: ArtifactTypeEnum
    path: str

class ArtifactCreate(ArtifactBase):
    file: UploadFile



