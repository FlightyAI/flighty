# Triton for Tritons

This repository contains code for heterogenous scaling of Triton: scaling to multiple replicas without loading every single model into memory in every single replica of Triton.


## Running Triton in just Docker

First build the Triton Docker image and run it locally.

```
docker build . -t gvashishtha/flighty:triton
docker run --rm -p8000:8000 -p8001:8001 -p8002:8002 gvashishtha/flighty:triton 
```
And run a readiness request:

`
 curl -v localhost:8000/v2/health/ready

 `
and run an inference request:
```
docker run -it --rm --net=host nvcr.io/nvidia/tritonserver:22.06-py3-sdk
/workspace/install/bin/image_client -m densenet_onnx -c 3 -s INCEPTION /workspace/images/mug.jpg
```

## Run Prometheus (localhost)

Prometheus needs to consume the metrics coming off the pod in order for us to visualize those metrics in Grafana.
```
docker build . -f prometheus.dockerfile -t gvashishtha/flighty:prometheus
docker run -p 9090:9090 gvashishtha/flighty:prometheus
```

## Install Grafana

For Mac:

```
brew update
brew install grafana
brew services start grafana
```

Right now the image has models baked in. Once we're comfortable with the models we'll want to mount them.

## Run Triton in a deployment

Now take the image you just built and run it in a deployment

```
k create -f triton/triton-deployment.yaml
```

Expose the pods: `k expose pod/<POD NAME>`

Port forward: `k port-forward services/triton-inference-server-85b79f6b6-g8cl9 8000:8000 8001:
8001 8002:8002`

Then do the load test again:

`python python_client.py`


## Deploy with Helm chart

`./initialize_helm.sh`

## Run a Horizontal Pod Autoscaler

Move the deployment to a helm chart and deploy both pieces together. Confirm that a second replica does spin up when using busybox to create load.

## Write code that can listen for the scale up event

## Write code that can get the GPU requirements of all models AND the number of requests

We'll need to reimplement BOTH the scheduler and the horizontal pod autoscaler

Maybe we hook into Grafana?

## Write model scheduler

https://thenewstack.io/a-deep-dive-into-kubernetes-scheduling/

## Write model autoscaler

Look for queue time from Prometheus. When it starts to go above threshold, load model into new GPU.
https://github.com/triton-inference-server/server/blob/main/docs/metrics.md

