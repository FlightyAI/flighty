# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

COPY setup.py /code/

# Ensure that subpackages can use absolute imports
RUN pip install -e .

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY *.py /code/

COPY *.yaml /code/

COPY routers /code/routers

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
