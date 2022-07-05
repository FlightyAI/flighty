# Local setup

## Install minikube

https://minikube.sigs.k8s.io/docs/start/

## Serve image locally

Use kubectl's Docker daemon because our images aren't in a public registry:
https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube

Apply the template:
`kubectl apply -f pod-create.yaml`

Expose the service on localhost:
https://minikube.sigs.k8s.io/docs/handbook/accessing/#example-of-nodeport
