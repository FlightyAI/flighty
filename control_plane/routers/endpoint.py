'''endpoint.py - CRUD methods for /endpoints subpath in FAST API '''
from urllib.parse import urlparse

import logging
import re
import uvicorn

import models
import schemas
from database import get_db
from kubernetes_api import create_virtual_service, create_destination_rule

from fastapi import Depends, APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

app =  APIRouter(prefix="/endpoints")


logger = logging.getLogger('endpoint')

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
    db_endpoint = db.query(models.Endpoint).filter(
        models.Endpoint.name == name).first()
    if db_endpoint:
        raise HTTPException(status_code=400, detail=f"Endpoint with name {name} "
            "already exists.")
    logger.debug("we're about to create destination rule")
    #create_destination_rule(endpoint_name=name)
    create_virtual_service(endpoint_name=name)

    db_endpoint = models.Endpoint(name=name)
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)

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




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
