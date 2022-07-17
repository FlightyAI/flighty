#!/bin/bash

kubectl create -f namespace.yaml
helm install flighty-cp helm-chart --namespace=flighty-ai