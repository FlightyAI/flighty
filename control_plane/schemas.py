"""
schemas.py

Database schemas for Flighty control plane objects, used in type hints
"""

from typing import Union
from fastapi import UploadFile
from models import ArtifactTypeEnum

from pydantic import AnyUrl, BaseModel


class ArtifactBase(BaseModel):
    '''Base class for artifact'''
    name: str
    version: int
    type: ArtifactTypeEnum
    path: Union[str, None] = None

class ArtifactCreate(ArtifactBase):
    '''Used for artifact_create() method'''
    file: UploadFile

class Artifact(ArtifactBase):
    '''Returned from Artifact list method'''

    class Config:
        '''Datbase config'''
        orm_mode = True

class EndpointBase(BaseModel):
    '''Endpoint base class'''
    name: str

class EndpointCreate(EndpointBase):
    '''Class to be used to create endpoint'''
    pass

class Endpoint(EndpointBase):
    '''Returned from endpoint list method'''
    url: AnyUrl

    class Config:
        '''Database config'''
        orm_mode = True

class HandlerBase(BaseModel):
    '''Handler base class'''
    name: str
    version: int
    endpoint: str
    docker_image: str

class Handler(HandlerBase):
    class Config:
        '''Database config'''
        orm_mode = True