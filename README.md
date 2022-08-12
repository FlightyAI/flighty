# Cloud setup

## Create AKS cluster

`az group create --name AzureRg --location northcentralus`

```
az aks create -g AzureRg -n FlightyAKS \
--node-count 1 \
  --generate-ssh-keys \
  	--enable-cluster-autoscaler \
	--min-count 1 \
	--max-count 1
```

## Set correct kubeconfig and Azure context

```
k config use-context FlightyAKS
az account set --name 'Microsoft Azure Sponsorship'
az config set defaults.group=AzureRg

```

## Add spot node pool
```
az aks nodepool add \
    	--cluster-name FlightyAKS \
    	--name nodepool \
    	--node-vm-size Standard_A2_v2 \
    	--node-count 1 \
    	--node-osdisk-size 30 \
    	--enable-cluster-autoscaler \
    	--min-count 0 \
    	--max-count 3

```
Taint the system node pool so we only use spot node pool (I think this might resolve permissions issues in mySQL container)

`k taint nodes aks-nodepool1-31754575-vmss000000 CriticalAddonsOnly=true:NoSchedule`

## Connect to cluster:

`az aks get-credentials --resource-group AzureRg --name FlightyAKS `

Register Azure storage provider:

`az provider register --namespace Microsoft.Storage`

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

Note that kiali won't be able to schedule on spot node pool, so you'll need to edit the deployment to add:

```
      tolerations:
        - key: "kubernetes.azure.com/scalesetpriority"
          operator: "Equal"
          value: "spot"
          effect: "NoSchedule"
```

and then delete the pods to force this toleration to be applied.

### Install and configure istio

Create the gateway
`kubectl create -f istio-gateway.yaml`

Add the virtual services:

`kubectl create -f virtual-service.yaml`
