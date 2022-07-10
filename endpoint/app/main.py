from fastapi import FastAPI
from kubernetes import client, config
from typing import Union
import MySQLdb

app = FastAPI()
db = MySQLdb.connect(
    # TODO - avoid hardcoding namespace, will want to be configurable
    # TODO - use secret password
    # host="mysql.default.svc.cluster.local", 
    host="192.168.65.4",
    port=3306, 
    password="password",
    db="test")
c=db.cursor()


@app.get("/show_endpoints")
def read_root():
    c.execute("""SELECT * FROM endpoints""")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()

v1 = client.CoreV1Api()


@app.post("/create_handler")
def create_pod():
  containers = [client.V1Container(name='test', image='docker.io/gvashishtha/flighty:test')]
  spec = client.V1PodSpec(
      containers=containers, 
      image_pull_secrets=[client.V1LocalObjectReference(name='regcred')])
  metadata=client.V1ObjectMeta(name='test1', labels={"pod_type": "mlservice"})
  pod = client.V1Pod(metadata=metadata, spec=spec)
  v1.create_namespaced_pod(namespace='default', body=pod)
