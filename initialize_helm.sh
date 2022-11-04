#!/bin/bash

# Uncomment this line if deploying to Azure
# kubectl config use-context FlightyAKS
kubectl create -f namespace.yaml
helm install flighty-cp helm-chart -f helm-chart/values_local.yaml --namespace=flighty-ai

# for deploying to Azure, do
# helm install flighty-cp helm-chart -f helm-chart/values.yaml --namespace=flighty-ai