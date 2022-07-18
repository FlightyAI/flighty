'''endpoint.py - CRUD methods for /endpoints subpath in FAST API '''
from urllib.parse import urlparse

import logging
import re
import uvicorn

import crud
import kubernetes_api as kapi
import models
import schemas
from database import get_db

from fastapi import Depends, APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

app =  APIRouter(prefix="/endpoints")


logger = logging.getLogger('endpoint')


def raise_if_endpoint_exists(db, name):
    '''Raises 400 error if endpoint exists'''

    if crud.endpoint_exists(db, name):
        raise HTTPException(status_code=400, detail=f"""Endpoint with name {name} "
            already exists""")

def raise_if_endpoint_does_not_exist(db, name):
    '''Raises 400 error if endpoint does not exist'''

    if not(crud.endpoint_exists(db, name)):
        raise HTTPException(status_code=400, detail=f"""Endpoint with name {name} "
            does not exist""")

def raise_if_associated_handlers(db, name):
    '''Raises 400 error if endpoint has handlers associated with it'''
    db_endpoint = crud.get_endpoint(db=db, name=name)
    if (len(db_endpoint.handlers) != 0):
        raise HTTPException(status_code=400, detail=f"""Endpoint with name {name}
            has associated handlers {db_endpoint.handlers}.
            The endpoint cannot be deleted until those handlers are also deleted.""")

@app.post("/create", response_model=schemas.Endpoint)
def create_endpoint(
        endpoint: schemas.EndpointCreate,
        req: Request,
        db: Session = Depends(get_db)):
    '''Creates the specified endpoint, fails if it already exists'''
    name = endpoint.name
    parsed_uri = urlparse(req.url._url)  # pylint: disable=protected-access
    base_path = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)

    if not(re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$', name)):
        raise HTTPException(status_code=422, detail=f"""Endpoint name {name} is not valid.
            A lowercase RFC 1123 subdomain must consist of lower case alphanumeric characters,
            '-' or '.', and must start and end with an alphanumeric character (e.g. 'example.com', 
            regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')""")
    raise_if_endpoint_exists(db=db, name=name)

    logger.debug("we're about to create destination rule")
    #create_destination_rule(endpoint_name=name)
    kapi.create_virtual_service(endpoint_name=name)

    crud.create_endpoint(db=db, name=name)

    url=(base_path + name)
    logger.debug("url is %s", url)

    returned_endpoint = schemas.Endpoint(name=name, url=url)
    return returned_endpoint

@app.get("/list")
async def list_endpoints(name: str = None, db: Session = Depends(get_db)):
    '''Lists all endpoints that exist, optionally filtering by name'''
    logger.debug("we're listing endpoints")
    if name:
        return db.query(models.Endpoint).filter_by(name=name).all()
    else:
        return db.query(models.Endpoint).all()


@app.delete("/delete")
async def delete_endpoint(endpoint: schemas.Endpoint, db: Session = Depends(get_db)):
    '''Validates that Endpoint exists, then deletes from DB'''

    # Do some validation
    raise_if_endpoint_does_not_exist(db=db, name=endpoint.name)
    raise_if_associated_handlers(db=db, name=endpoint.name)

    # Delete virtual service   
    kapi.delete_virtual_service(endpoint_name=endpoint.name)

    # Finally, delete from DB
    crud.delete_endpoint(db=db, name=endpoint.name)

    return f"Endpoint {endpoint.name} successfully deleted."    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
