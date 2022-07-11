from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

import mysql.connector
import os

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

class Artifact(BaseModel):
    name: str
    version: int = 0
    file: UploadFile
    type: str

# Write file to subpath of mounted volume
# Then store this path inside of database
# We'll then mount that volume to containers we spin up
@app.post("/create")
async def create_artifact(file: UploadFile, name: str, version: int, type: str):
    dir_path = f'./flighty-files/{name}/{version}'
    os.makedirs(dir_path, exist_ok=True)
    with open(f'{dir_path}/{file.filename}', 'wb') as f:
        f.write(file.file.read())




@app.post("/create_handler")
def create_pod():
  containers = [client.V1Container(name='handler', image='docker.io/gvashishtha/flighty:handler')]
  spec = client.V1PodSpec(
      containers=containers, 
      image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
  metadata=client.V1ObjectMeta(name='test1', labels={"flighty": "mlservice-cpu"})
  pod = client.V1Pod(metadata=metadata, spec=spec)
  v1.create_namespaced_pod(namespace='default', body=pod)
