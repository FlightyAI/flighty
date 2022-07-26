#!/bin/bash

kubectl create -f namespace.yaml
helm install flighty-triton helm-chart --namespace=flighty-ai