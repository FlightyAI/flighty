from fastapi import FastAPI, HTTPException
import json
from kubernetes import client, config
from pydantic import BaseModel
from typing import Union

import mysql.connector

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

class Handler(BaseModel):
    name: str
    endpoint: str
    docker_image: str = 'python'
    folder_path: str
    prod_traffic: int = 0
    shadow_traffic: int = 0

@app.post("/create")
async def create_handler(handler: Handler):
    try:
        c.execute("SELECT id FROM endpoints WHERE name = %s", (handler.endpoint, ))
        if c.row_count == 0:
            raise HTTPException(status_code=404, detail=f"Endpoint {handler.endpoint} not found")
        endpoint_id = c.fetchone()['id']

        # Decide whether this is the first handler behind a given endpoint
        c.execute("SELECT COUNT(*) AS total FROM handlers WHERE endpoint_id = %s", (endpoint_id,))
        handler.prod_traffic = 100 if c.fetchall()[0]['total'] == 0 else 0
        handler.shadow_traffic = 0

        c.execute(
            """INSERT INTO handlers 
            (name, folder_path, docker_image, prod_traffic, shadow_traffic, endpoint_id) VALUES (%s, %s, %s, %s, %s, %s)
            """, (handler.name, handler.folder_path, handler.docker_image, 
                handler.prod_traffic, handler.shadow_traffic, endpoint_id))
        cnx.commit()
        return handler
    except Exception as e:
        print(e)



# Configs can be set in Configuration class directly or using helper utility
try:
    config.load_incluster_config()
except Exception as e:
    print(e)

v1 = client.CoreV1Api()


@app.post("/create_handler")
def create_pod():
  containers = [client.V1Container(name='handler', image='docker.io/gvashishtha/flighty:handler')]
  spec = client.V1PodSpec(
      containers=containers, 
      image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
  metadata=client.V1ObjectMeta(name='test1', labels={"flighty": "mlservice-cpu"})
  pod = client.V1Pod(metadata=metadata, spec=spec)
  v1.create_namespaced_pod(namespace='default', body=pod)
