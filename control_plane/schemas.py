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

class ArtifactReturn(ArtifactBase):
    path: Union[str, None] = None
    type: ArtifactTypeEnum

class ArtifactCreate(ArtifactReturn):
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

class EndpointDelete(EndpointBase):
    '''Class to be used to delete endpoint'''
    pass

class Endpoint(EndpointBase):
    '''Returned from endpoint list method'''
    url: AnyUrl = ''

    class Config:
        '''Database config'''
        orm_mode = True

class HandlerBase(BaseModel):
    '''Handler base class'''
    name: str
    version: int = 0
    endpoint: str
    docker_image: str = 'docker.io/gvashishtha/flighty:model_server'

class HandlerDelete(HandlerBase):
    '''For deleting handlers'''
    pass

class Handler(HandlerBase):
    class Config:
        '''Database config'''
        orm_mode = True

class HandlerCreate(HandlerBase):
    model_artifact: str
    code_artifact: str
    model_artifact_version: int = None
    code_artifact_version: int = None
    version: int = None