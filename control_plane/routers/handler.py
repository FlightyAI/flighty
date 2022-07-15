"""
handler.py

Contains the functionality for the /handlers path of the Fast API endpoint
"""

import models
import schemas

from kubernetes_api import create_deployment, create_service


import uvicorn

from database import get_db
from fastapi import Depends, APIRouter, HTTPException

from sqlalchemy.orm import Session

app = APIRouter(prefix="/handlers")



@app.post("/create", response_model=schemas.Handler)
def create_handler(
        model_artifact: str,
        code_artifact: str,
        endpoint_name: str,
        name: str,
        model_artifact_version: int = None,
        code_artifact_version: int = None,
        docker_image: str = 'docker.io/gvashishtha/flighty:model_server',
        version: int = None,
        db: Session = Depends(get_db)):
    """
    create_handler

    Creates a handler behind the specified endpoint.
    """
    prod_traffic = shadow_traffic = 0
    db_endpoint = db.query(models.Endpoint).filter(
        models.Endpoint.name == endpoint_name).first()
    if not db_endpoint:
        raise HTTPException(status_code=400, detail=f"""Endpoint with name {endpoint_name} "
           does not exist""")
    db_endpoint_id = db_endpoint.id
    cur_max = len(db.query(models.Handler).filter(
            models.Handler.id == db_endpoint_id,
            models.Handler.name == name).all()) - 1
    if cur_max == -1: # this is the first model of this version
        version = 0
        prod_traffic = 100
    if version <= cur_max:
        raise HTTPException(status_code=400, detail=f"""You specified a version of {version}
        but the largest one we have is {cur_max}. Please specify a version greater 
        than {cur_max} and try again.""")
    db_handler = db.query(models.Handler).filter(
        models.Handler.id == db_endpoint_id,
        models.Handler.name == name,
        models.Handler.version == version).first()
    if db_handler:
        raise HTTPException(status_code=400, detail=f"Handler with name {name} "
            f"and version {version} already exists")

    # TODO - add logic to autopopulate code and model version numbers with maxima

    model_artifact =  db.query(models.Artifact).filter(
        models.Artifact.name == model_artifact,
        models.Artifact.version == model_artifact_version,
        models.Artifact.type == models.ArtifactTypeEnum.model).first()
    if not model_artifact:
        raise HTTPException(status_code=400, detail=f"Model artifact with name {model_artifact} "
            f"does not yet exist")

    code_artifact =  db.query(models.Artifact).filter(
        models.Artifact.name == code_artifact,
        models.Artifact.version == code_artifact_version,
        models.Artifact.type == models.ArtifactTypeEnum.code).first()
    if not code_artifact:
        raise HTTPException(status_code=400, detail=f"Code artifact with name {code_artifact} "
            f"does not yet exist")

    db_handler = models.Handler(name=name, version=version,
        docker_image=docker_image, endpoint_id=db_endpoint_id,
        prod_traffic=prod_traffic, shadow_traffic=shadow_traffic)
    db_handler.artifacts.append(code_artifact)
    db_handler.artifacts.append(model_artifact)


    create_deployment(handler_name=name, model_artifact=model_artifact.name,
    model_version=model_artifact.version, code_artifact=code_artifact.name,
    code_version=code_artifact.version)
    create_service(handler_name=name)

    db.add(db_handler)
    db.commit()
    db.refresh(db_handler)

    return schemas.Handler(
        name=name, version=version, endpoint_name=endpoint_name, 
        docker_image=docker_image)



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
