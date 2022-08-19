#!/bin/bash

kubectl config use-context docker-desktop
kubectl create -f namespace.yaml
helm install flighty-cp helm-chart --namespace=flighty-ai -f ./helm-chart/values_local.yaml
kubectl config set-context --current --namespace=flighty-ai