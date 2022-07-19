# Model server

This is the base model server within which we run customers' code.

It has to do two things:
1. Mount the customer's code and model artifacts in well-known locations
1. Run the init() method that the customer provided once
1. Run the predict() method that the customer provided on every request.

## Build and push Docker image

```
docker build . -t gvashishtha/flighty:model_server
docker push gvashishtha/flighty:model_server
```

## Running to test

```
docker run -p 8001:80 -v /Users/gkv/Startup/flighty/model_server/customer_code:/code/customer_code \
-v /Users/gkv/Startup/flighty/model_server:/code/flighty-files/first-artifact/2 \
  gvashishtha/flighty:model_server 
```

## Running on cluster

NOTE - we must unpack _files_ at the customer_code folder. If you zip a directory, you'll get too many
layers of nesting and the relative imports will not work. So in the SDK we also need to be mindful of how
we handle uploads.

```
kubectl create -f k8s-yaml/pod-create.yaml
kubectl expose pod/test --port 80
kubectl port-forward service/test 8001:80
```

then you can see the docs at localhost:8001/docs