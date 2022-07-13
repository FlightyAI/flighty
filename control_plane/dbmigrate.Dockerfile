# 
FROM python:3.9

COPY ./requirements.txt /code/requirements.txt

COPY *.py /code
# 
WORKDIR /code

# Ensure that subpackages can use absolute imports
RUN pip install -e .

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY alembic.ini /code/

COPY alembic /code/alembic

ENTRYPOINT ["alembic"]
