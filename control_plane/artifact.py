from contextlib import closing
from enum import Enum
from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from pydantic import BaseModel, PositiveInt
from sqlalchemy.orm import Session

from control_plane.database import SessionLocal
from . import models, schemas

import mysql.connector
import os
import shutil
import uvicorn


# TODO - factor this out into shared library across all services
db_conn_info = {
    "user": "root",
    "password": "password",
    "host": "mysql.default.svc.cluster.local",
    "database": "flighty"
}


def discover_host():
    try:   
        cnx = mysql.connector.connect(**db_conn_info)
    except mysql.connector.errors.DatabaseError:
        try:
            # Attempt to connect to localhost if we are doing local development
            db_conn_info['host'] = '127.0.0.1'
            cnx = mysql.connector.connect(**db_conn_info)
            
        except mysql.connector.errors.DatabaseError:
            # if we're running in Docker
            db_conn_info['host'] = 'host.docker.internal'
            cnx = mysql.connector.connect(**db_conn_info)
    finally:
        cnx.close()


discover_host()

app = FastAPI()

class ArtifactTypeEnum(str, Enum):
    code = 'code'
    model = 'model'

class Artifact(BaseModel):
    name: str
    version: PositiveInt = 1
    path: str
    type: ArtifactTypeEnum

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/artifact/create", response_model=schemas.Artifact)
def create_art(artifact: schemas.ArtifactCreate, db: Session = Depends(get_db)):
    db_artifact = db.query(models.Artifact).filter(models.User.email == email).first()
    if db_artifact:
        raise HTTPException(status_code=400, detail=f"Artifact with name {artifact.name} "
            f"and version {artifact.version} already exists")
    db_artifact = models.Artifact(name=artifact.name, version=artifact.version, 
        path=artifact.file.filename, type=artifact.type)
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact

# Write file to subpath of mounted volume
# Then store the full path inside of the database
# We'll then mount that volume to containers we spin up
@app.post("/create")
async def create_artifact(
        file: UploadFile = Form(...), 
        name: str = Form(...), 
        version: PositiveInt = Form(...), 
        type: ArtifactTypeEnum = Form(...)):
    ()
    db_path = os.path.join('flighty-files', name, str(version))
    dir_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), db_path)
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, file.filename)

    # TODO - There is a dependency between where artifact is writing files and where 
    # handler expects to read them
    # Need to figure out a way to factor that dependency into one common place
    artifact = Artifact(name=name, version=version, path='/' + db_path, type=type)
    print(f'artifact is {artifact}')
    with closing(mysql.connector.connect(**db_conn_info)) as cnx:
        with closing(cnx.cursor(dictionary=True)) as c:
            try:
                c.execute(
                        """INSERT INTO artifacts
                        (name, path, version, type) VALUES (%s, %s, %s, %s)
                        """, (artifact.name, artifact.path, artifact.version, 
                            artifact.type)
                )
                cnx.commit()
            except mysql.connector.errors.IntegrityError:
                c.execute("SELECT MAX(version) AS max FROM artifacts WHERE name = %s", (artifact.name,))
                last_version = c.fetchone()['max']
                raise HTTPException(status_code=422, detail=f"""Artifact {name} with version 
                    {version} already exists. 
                    Specify a version larger than {last_version} and try again.""")

    with open(path, 'wb') as f:
        f.write(file.file.read())
        print(f'wrote file out to path {path}')
    
    try:
        shutil.unpack_archive(path, dir_path) # unpack zip file if it is a zip
        os.remove(path)
    except shutil.ReadError as e: # not a zip file
        pass

    return artifact


@app.get("/list")
async def list_artifacts(name: str = None):
    with closing(mysql.connector.connect(**db_conn_info)) as cnx:
        with closing(cnx.cursor(dictionary=True)) as c:
            if name:
                c.execute("SELECT * FROM artifacts WHERE name = %s", (name,))
                return c.fetchall()
            else:
                c.execute("SELECT * FROM artifacts")
                return c.fetchall()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# docker run -p 80:80 -v /Users/gkv/Startup/flighty/artifact/flighty-files:/code/flighty-files gvashishtha/flighty:artifact