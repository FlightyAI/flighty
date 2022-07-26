#!/bin/bash

helm uninstall flighty-triton
kubectl delete -f namespace.yaml