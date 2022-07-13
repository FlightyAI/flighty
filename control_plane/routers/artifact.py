import models
import schemas
from database import SessionLocal

from fastapi import Depends, APIRouter, File, Form, HTTPException, UploadFile
from pydantic import PositiveInt
from sqlalchemy.orm import Session

import logging
import os
import shutil
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('artifact')

app =  APIRouter(prefix="/artifacts")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create", response_model=schemas.Artifact)
def create_artifact(
        file: UploadFile = File(...), 
        name: str = Form(...), 
        version: PositiveInt = Form(...), 
        type: models.ArtifactTypeEnum = Form(...), 
        db: Session = Depends(get_db)):
    db_path = os.path.join('flighty-files', name, str(version))
    dir_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), db_path)
    path = os.path.join(dir_path, file.filename)
    db_artifact = db.query(models.Artifact).filter(
        models.Artifact.name == name,
        models.Artifact.version == version).first()
    if db_artifact:
        raise HTTPException(status_code=400, detail=f"Artifact with name {name} "
            f"and version {version} already exists")
    db_artifact = models.Artifact(name=name, version=version, 
        path=file.filename, type=type)
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)

    # Write file to mounted volume in a place that handlers 
    # will be able to find it
    os.makedirs(dir_path, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(file.file.read())
        logger.info(f'wrote file out to path {path}')
    
    # unpack zip file if it is a zip
    try:
        shutil.unpack_archive(path, dir_path) 
        logger.info('archive deteced, unpacking...')
        os.remove(path)
    except shutil.ReadError as e: # not a zip file
        pass
    return db_artifact

@app.get("/list")
async def list_artifacts(name: str = None, db: Session = Depends(get_db)):
    if name:
        return db.query(models.Artifact).filter_by(name=name).all()
    else:
        return db.query(models.Artifact).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
