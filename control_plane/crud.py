'''CRUD operations for models, artifacts, and handlers'''

import models

from fastapi import  HTTPException


def artifact_exists(db, name, version):
    '''Returns True if artifact already exists'''

    db_artifact = get_artifact(db=db, name=name, version=version)
    return (db_artifact is not None)


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