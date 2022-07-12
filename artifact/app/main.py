from enum import Enum
from fastapi import FastAPI, Form, HTTPException, UploadFile
from pydantic import BaseModel, PositiveInt

import mysql.connector
import os
import shutil
import uvicorn


# TODO - factor this out into shared library across all services
try:   
    cnx = mysql.connector.connect(host="mysql.default.svc.cluster.local", password="password", database="flighty")
except mysql.connector.errors.DatabaseError:
    try:
        # Attempt to connect to localhost if we are doing local development
        cnx = mysql.connector.connect(host="127.0.0.1", password="password", database="flighty")
    except mysql.connector.errors.DatabaseError:
        # if we're running in Docker
        cnx = mysql.connector.connect(host="host.docker.internal", password="password", database="flighty")

c=cnx.cursor(dictionary=True)

app = FastAPI()

class ArtifactTypeEnum(str, Enum):
    code = 'code'
    model = 'model'

class Artifact(BaseModel):
    name: str
    version: PositiveInt = 1
    path: str
    type: ArtifactTypeEnum

# Write file to subpath of mounted volume
# Then store the full path inside of the database
# We'll then mount that volume to containers we spin up
@app.post("/create")
async def create_artifact(
        file: UploadFile = Form(...), 
        name: str = Form(...), 
        version: PositiveInt = Form(...), 
        type: ArtifactTypeEnum = Form(...)):
    db_path = os.path.join('flighty-files', name, str(version))
    dir_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), db_path)
    os.makedirs(dir_path, exist_ok=True)

    path = os.path.join(dir_path, file.filename)

    # TODO - There is a dependency between where artifact is writing files and where handler expects to read them
    # Need to figure out a way to factor that dependency into one common place
    artifact = Artifact(name=name, version=version, path='/' + db_path, type=type)

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
        raise HTTPException(status_code=422, detail=f"""Artifact {name} with version {version} already exists. 
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
    if name:
        c.execute("SELECT * FROM artifacts WHERE name = %s", (name,))
        return c.fetchall()
    else:
        c.execute("SELECT * FROM artifacts")
        return c.fetchall()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# curl -X POST "http://localhost:80/create" -H "accept: application/json" \
#  -H "Content-Type: multipart/form-data" -F "file=@requirements.txt" \
#  -F "name=test" -F "type=code" -F "version=3"