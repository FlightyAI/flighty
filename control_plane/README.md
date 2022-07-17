## Make database migration

Do this after changing the database model in database.py

```
alembic revision --autogenerate -m "<commit name>"
alembic upgrade head
```

## Testing Python code locally

The fastest way to make sure that your Python code is actually working the way you intend
is to develop locally. First, make sure your SQL server is exposed at port 3306, by running

`kubectl port-forward service/mysql-external 3306:3306`.

Then use your debugger on the main.py file for fast apiyou've been developing.


## Build Control Plane docker image

We need to mount the artifacts directories and the kubeconfig directories in the expected locations.
```
docker build . -t gvashishtha/flighty:controlplane
docker run -p 8000:80 -v /Users/gkv/Startup/flighty/flighty-files:/code/flighty-files \
  -v ~/.kube/config:/kube/config --env KUBECONFIG=/kube/config --env DB_URL=host.docker.internal \
  --env GATEWAY_NAMESPACE=default --env K8S_NAMESPACE=flighty-ai \
  --env GATEWAY_NAME=flighty-control-plane \
  gvashishtha/flighty:controlplane 
```

## Build alembic Docker image

```
docker build . -f dbmigrate.Dockerfile -t gvashishtha/flighty:alembic
docker run --env DB_URL=host.docker.internal \
  gvashishtha/flighty:alembic upgrade 26dd889ef799
```

## Pushing

Make sure to push both images once satisfied with local testing:

```
docker push gvashishtha/flighty:controlplane
docker push gvashishtha/flighty:alembic
```