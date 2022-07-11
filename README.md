# Local setup

## Install minikube

https://minikube.sigs.k8s.io/docs/start/

## Create pod

Use private registry credentials:
https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/

Apply the template:
`kubectl apply -f pod-create.yaml`

## Give sufficient permissions to default service account for it to create pods

```
kubectl apply -f pod-role.yaml
kubectl apply -f pod-rolebinding.yaml
```

## Deploy database

`kubectl apply -f k8s-mysql/mysql-deployment.yaml`

### Expose pod on localhost

Directions are [from here](https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/):

```
kubectl port-forward service/mysql-external 3306:3306
```

Access at this location: `http://127.0.0.1:TUNNEL_PORT`

Send a POST request to test creation of pod (just go to /docs and do it through UI)
