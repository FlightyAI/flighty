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