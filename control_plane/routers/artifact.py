import crud
import file_io
import models
import schemas
from database import get_db

from fastapi import Depends, APIRouter, File, Form, UploadFile
from sqlalchemy.orm import Session

import logging
import uvicorn

logger = logging.getLogger('artifact')

app =  APIRouter(prefix="/artifacts")


@app.post("/create", response_model=schemas.ArtifactReturn)
def create_artifact(
        file: UploadFile = File(...), 
        name: str = Form(...), 
        version: int = Form(...), 
        type: models.ArtifactTypeEnum = Form(...), 
        db: Session = Depends(get_db)):

    crud.raise_if_artifact_exists(db, name, version)

    artifact_dir_path = file_io.write_artifact(file=file, name=name, version=version)

    crud.create_artifact(db, name=name, version=version, path=artifact_dir_path, type=type)

    return_artifact = schemas.ArtifactReturn(name=name, version=version, type=type, path=artifact_dir_path)
    return return_artifact

@app.get("/list")
async def list_artifacts(name: str = None, db: Session = Depends(get_db)):
    if name:
        return db.query(models.Artifact).filter_by(name=name).all()
    else:
        return db.query(models.Artifact).all()

@app.delete("/delete")
async def delete_artifact(artifact: schemas.Artifact, db: Session = Depends(get_db)):
    '''Validates that artifact exists, then deletes from filesystem and DB'''

    # Do some validation
    crud.raise_if_artifact_does_not_exist(db=db, name=artifact.name, version=artifact.version)
    crud.raise_if_associated_handlers(db=db, name=artifact.name, version=artifact.version)

    # Delete from file storage
    file_io.delete_artifact(db=db, name=artifact.name, version=artifact.version)

    # Finally, delete from DB
    crud.delete_artifact(db=db, name=artifact.name, version=artifact.version)

    return f"Artifact {artifact.name} with version {artifact.version} successfully deleted."    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
