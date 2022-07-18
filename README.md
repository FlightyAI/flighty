# Local setup

## Running tests

Setup with: `./initialize_helm.sh`

Clean up with: `./clean-up_helm.sh`

## Deploy with Helm

```
helm install flighty-cp helm-chart --namespace=flighty-ai
```
Then open up the URL
`127.0.0.1/api/v1/docs` and you should see the application. If you get a 503 saying 
  ```
  upstream connect error or disconnect/reset before headers. 
  reset reason: connection termination
  ```, 
what finally solved it for me was to just uninstall and reinstall istio.

### Uninstalling and reinstalling istio

Uninstall istio: `istioctl x uninstall --purge`

Install again: `istioctl install`
Recreate gateway in default namespace: 

```
kubectl config set-context --current --namespace=default
kubectl apply -f istio-gateway.yaml
kubectl config set-context --current --namespace=flighty-ai
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

First install Prometheus for Istio add-on:
`kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.14/samples/addons/prometheus.yaml`

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

## Generate SDK

Install swagger code gen:

`brew install swagger-codegen`

Then generate the Python SDK:

`swagger-codegen generate -i http://localhost/api/v1/openapi.json -l python -o generated-python`

and install the Python SDK:

`python3 setup.py install --user`

Then open a Python REPL and upload an artifact:

```
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
file = 'README.md' # str | 
name = 'name_example' # str | 
version = 56 # int | 
type = swagger_client.ArtifactTypeEnum().MODEL

api_instance.create_artifact_artifacts_create_post('README.md', name, version, type)
```