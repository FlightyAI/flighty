"""
handler.py

Contains the functionality for the /handlers path of the Fast API endpoint
"""
import crud
import models
from requests import delete
import schemas

from kubernetes_api import create_deployment, create_service, \
    add_handler_to_endpoint, delete_deployment, delete_service
from .artifact import list_artifacts
from .endpoint import raise_if_endpoint_does_not_exist, raise_if_endpoint_exists

import logging
import uvicorn

from database import get_db
from fastapi import Depends, APIRouter, HTTPException

from sqlalchemy.orm import Session

app = APIRouter(prefix="/handlers")

logger = logging.getLogger('artifact')


def raise_if_handler_does_not_exist(db, name, version, endpoint):
    '''Raises 400 error if handler does not exist'''

    if not(crud.handler_exists(db, name, version, endpoint)):
        raise HTTPException(status_code=400, detail=f"""Handler with name {name}
            and version {version} does not exist behind endpoint {endpoint}""")

@app.delete("/delete")
def delete_handler(
    handler: schemas.HandlerDelete,
    db: Session = Depends(get_db)):
    # Raise if it does not exist
    raise_if_handler_does_not_exist(db,
        name=handler.name, version=handler.version, endpoint=handler.endpoint)

    # TODO: Raise if shadow traffic or prod traffic are not 0
    # TODO: modify traffic rules
    # Delete deployment
    delete_deployment(endpoint_name=handler.endpoint, handler_name=handler.name, 
        handler_version=handler.version)
    delete_service(endpoint_name=handler.endpoint,
        handler_name=handler.name, handler_version=handler.version)

    # Finally delete from database
    crud.delete_handler(db, name=handler.name, version=handler.version, endpoint=handler.endpoint)

@app.post("/create", response_model=schemas.Handler)
def create_handler(
        handler: schemas.HandlerCreate,
        db: Session = Depends(get_db)):
    """
    create_handler

    Creates a handler behind the specified endpoint.
    """
    prod_traffic = shadow_traffic = 0
    raise_if_endpoint_does_not_exist(db=db, name=handler.endpoint)

    endpoint = crud.get_endpoint(db=db, name=handler.endpoint)
    cur_max = len(endpoint.handlers) - 1
    if cur_max == -1: # this is the first model of this endpoint
        prod_traffic = 100
    if handler.version <= cur_max:
        raise HTTPException(status_code=400, detail=f"""You specified a version of
        {handler.version} but the largest one we have is {cur_max}. 
        Please specify a version greater than {cur_max} and try again.""")
    db_handler = db.query(models.Handler).filter(
        models.Handler.endpoint_id == endpoint.id,
        models.Handler.name == handler.name,
        models.Handler.version == handler.version).first()
    if db_handler:
        raise HTTPException(status_code=400, detail=f"Handler with name {handler.name} "
            f"and version {handler.version} already exists")

    # TODO - add logic to autopopulate code and model version numbers with maxima

    model_artifact =  db.query(models.Artifact).filter(
        models.Artifact.name == handler.model_artifact,
        models.Artifact.version == handler.model_artifact_version,
        models.Artifact.type == models.ArtifactTypeEnum.model).first()
    if not model_artifact:
        raise HTTPException(status_code=400, detail=f"Model artifact with name {model_artifact} "
            f"does not yet exist")

    code_artifact =  db.query(models.Artifact).filter(
        models.Artifact.name == handler.code_artifact,
        models.Artifact.version == handler.code_artifact_version,
        models.Artifact.type == models.ArtifactTypeEnum.code).first()
    if not code_artifact:
        raise HTTPException(status_code=400, detail=f"Code artifact with name {code_artifact} "
            f"does not yet exist")

    db_handler = models.Handler(name=handler.name, version=handler.version,
        docker_image=handler.docker_image, endpoint_id=endpoint.id,
        prod_traffic=prod_traffic, shadow_traffic=shadow_traffic)
    db_handler.artifacts.append(code_artifact)
    db_handler.artifacts.append(model_artifact)

    logger.debug('sending %s as docker image', handler.docker_image)
    create_deployment(handler_name=handler.name, handler_version=handler.version,
        model_artifact=model_artifact.name, docker_image=handler.docker_image,
        model_version=model_artifact.version, code_artifact=code_artifact.name,
        code_version=code_artifact.version, endpoint_name=handler.endpoint)

    create_service(handler_name=handler.name, handler_version=handler.version,
        endpoint_name=handler.endpoint)
    add_handler_to_endpoint(endpoint_name=handler.endpoint, handler_name=handler.name,
        handler_version=handler.version)

    db.add(db_handler)
    db.commit()
    db.refresh(db_handler)

    return schemas.Handler(
        name=handler.name, version=handler.version, endpoint=handler.endpoint,
        docker_image=handler.docker_image)


@app.get("/get", response_model=schemas.HandlerGet)
async def get_handler(name: str, version: int, endpoint: str, 
    db: Session = Depends(get_db)):
    '''Get a handler if it exists or raise an error if not'''
    to_return = crud.get_handler(db=db, name=name, version=version,
        endpoint=endpoint)
    if to_return is None:
        raise HTTPException(status_code=400, detail=f"""Handler with name {name}
            and version {version} behind endpoint {endpoint}
            does not exist""")
    code_artifacts = await list_artifacts(type=schemas.ArtifactTypeEnum.code, db=db)
    model_artifacts = await list_artifacts(type=schemas.ArtifactTypeEnum.model, db=db)
    returning = schemas.HandlerGet(
        name=to_return.name, version=to_return.version, endpoint=endpoint,
        model_artifacts=model_artifacts,
        code_artifact=code_artifacts[0])
    return returning

@app.get("/list")
async def list_handlers(name: str = None, db: Session = Depends(get_db)):
    """
    list_handlers

    Lists all handlers behind an (optional) endpoint.
    """
    if name:
        return db.query(models.Handler).filter_by(name=name).all()
    else:
        return db.query(models.Handler).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
