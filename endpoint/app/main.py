from fastapi import FastAPI
from pydantic import BaseModel
#from kubernetes import client, config
from typing import Union
import mysql.connector

class Endpoint(BaseModel):
    name: str

app = FastAPI()
cnx = mysql.connector.connect(host="127.0.0.1", password="password", database="flighty")
c=cnx.cursor()


@app.get("/list")
def show_endpoints():
    c.execute("""SELECT * FROM endpoints""")
    return (c.fetchall())


@app.post("/create")
async def create_endpoint(endpoint: Endpoint):
    try:
        c.execute("INSERT INTO endpoints (name) VALUES (%s)", (endpoint.name, ))
        cnx.commit()
        return endpoint
    except mysql.connector.errors.IntegrityError:
        return f"Endpoint with name {endpoint.name} already exists"

@app.post("/delete")
async def delete_endpoint(endpoint: Endpoint):
    #try:
    c.execute("DELETE FROM `endpoints` WHERE name == %s", (endpoint.name, ))
    cnx.commit()
    return "Endpoint successfully deleted"
    # except mysql.connector.errors.IntegrityError:
    #     return f"Endpoint with name {endpoint.name} already exists"
    


# Configs can be set in Configuration class directly or using helper utility
# config.load_incluster_config()

# v1 = client.CoreV1Api()


# @app.post("/create_handler")
# def create_pod():
#   containers = [client.V1Container(name='test', image='docker.io/gvashishtha/flighty:test')]
#   spec = client.V1PodSpec(
#       containers=containers, 
#       image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
#   metadata=client.V1ObjectMeta(name='test1', labels={"pod_type": "mlservice"})
#   pod = client.V1Pod(metadata=metadata, spec=spec)
#   v1.create_namespaced_pod(namespace='default', body=pod)
