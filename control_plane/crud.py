'''CRUD operations for models, artifacts, and handlers'''

import models

from fastapi import  HTTPException
from sqlalchemy import delete


def artifact_exists(db, name, version):
    '''Returns True if artifact already exists'''

    db_artifact = get_artifact(db=db, name=name, version=version)
    return (db_artifact is not None)

def raise_if_artifact_exists(db, name, version):
    '''Raises 400 error if artifact exists'''

    if artifact_exists(db, name, version):
        raise HTTPException(status_code=400, detail=f"Artifact with name {name} "
            f"and version {version} already exists")

def raise_if_artifact_does_not_exist(db, name, version):
    '''Raises 400 error if artifact does not exist'''

    if not(artifact_exists(db, name, version)):
        raise HTTPException(status_code=400, detail=f"Artifact with name {name} "
            f"and version {version} does not exist")

def raise_if_associated_handlers(db, name, version):
    '''Raises 400 error if artifact has handlers associated with it'''
    db_artifact = get_artifact(db=db, name=name, version=version)
    if (len(db_artifact.handlers) != 0):
        raise HTTPException(status_code=400, detail=f"""Artifact with name {name}
            and version {version} has associated handlers {db_artifact.handlers}.
            Artifact cannot be deleted until those handlers are also deleted.""")

def delete_artifact(db, name, version):
    '''Deletes specified artifact'''
    obj_to_delete = get_artifact(db=db, name=name, version=version)
    db.delete(obj_to_delete)
    db.commit()

def create_artifact(db, name, version, path, type):
    db_artifact = models.Artifact(name=name, version=version, 
        path=path, type=type)
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)

def get_artifact(db, name, version):
    return db.query(models.Artifact).filter(
        models.Artifact.name == name,
        models.Artifact.version == version).first()