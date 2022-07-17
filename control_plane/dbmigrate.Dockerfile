# 
FROM python:3.9

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY alembic.ini /code/

COPY alembic /code/alembic

COPY database.py models.py setup.py /code/
# 
WORKDIR /code

# Ensure that subpackages can use absolute imports
RUN pip install -e .

ENTRYPOINT ["alembic"]
