#!/bin/bash

helm uninstall flighty-cp
kubectl delete -f namespace.yaml