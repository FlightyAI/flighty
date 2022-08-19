#!/bin/bash

k config use-context FlightyAKS
kubectl create -f namespace.yaml
helm install flighty-cp helm-chart --namespace=flighty-ai