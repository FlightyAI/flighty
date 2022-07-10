from fastapi import FastAPI
from kubernetes import client, config
from typing import Union

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
