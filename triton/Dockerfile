FROM nvcr.io/nvidia/tritonserver:22.06-py3

COPY model_repository /models

ENTRYPOINT ["tritonserver", "--model-repository=/models"]