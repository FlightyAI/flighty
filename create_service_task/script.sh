#!/bin/bash

aws ecs create-service \
    --task-definition flighty-demo:1 \
    --cli-input-json file://ecs-run-service.json