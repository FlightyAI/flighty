'''CRUD operations for models, artifacts, and handlers'''

import models

from fastapi import  HTTPException


def artifact_exists(db, name, version):
    '''Returns True if artifact already exists'''

    db_artifact = get_artifact(db=db, name=name, version=version)
    return (db_artifact is not None)


def endpoint_exists(db, name):
    '''Returns True if endpoint already exists'''

    db_endpoint = get_endpoint(db=db, name=name)
    return (db_endpoint is not None)


def get_endpoint(db, name):
    '''Returns the specified endpoint'''
    return db.query(models.Endpoint).filter(
        models.Endpoint.name == name).first()

def create_endpoint(db, name):
    db_endpoint = models.Endpoint(name=name)
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)

def delete_endpoint(db, name):
    '''Deletes specified endpoint'''
    obj_to_delete = get_endpoint(db=db, name=name)
    db.delete(obj_to_delete)
    db.commit()

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