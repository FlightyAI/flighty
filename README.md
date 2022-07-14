# Local setup

## Deploy with Helm

```
helm install flighty-cp helm-chart
```

## Port-forward to check database is up

`kubectl port-forward service/mysql-external 3306:3306`

Query the database in MySQL workbench to confirm the database is now serving.

## Port-forward control plane

`kubectl port-forward service/controlplane-external 8001:80`

## Upload required files

Open the web UI at 127.0.0.1:8001/docs and upload two files:

```
file: Artifact.zip (containing zipped Python main.py with init() and predict())
name: code-artifact
version: 1
type: code
```

```
file: Artifact.zip
name: first-artifact
version: 1
type: code
```

## Deploy and expose one-off service

```
kubectl create -f pod-create.yaml
kubectl port-forward service/test 8000:80  
```

Open the web UI at 127.0.0.1:8000/docs to see your service up and running.



## Install istio

### (optional) Install kiali for monitoring

```
helm install \                                            
  --namespace istio-system \
  --set auth.strategy="anonymous" \
  --repo https://kiali.org/helm-charts \
  kiali-server \
  kiali-server
kubectl port-forward svc/kiali 20001:20001 -n istio-system
```

### Install and configure istio

Create the gateway
`kubectl create -f istio-gateway.yaml`

Add the virtual services:

`kubectl create -f virtual-service.yaml`