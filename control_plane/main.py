'''Main router for Fast API app'''
import logging
import os

from fastapi import FastAPI
from routers import artifact, endpoint, handler

import uvicorn

logging.basicConfig(level=logging.DEBUG)

# We need a different root path when serving in cluster
app = FastAPI(root_path = os.environ.get("FAST_API_ROOT", "/"))

app.include_router(artifact.app)
app.include_router(endpoint.app)
app.include_router(handler.app)

@app.get("/")
async def root():
    '''Returns plaintext string, good for knowing we're alive '''
    return {"message": "This is the flighty root"}

# TODO - I think port contention here is what's messing up istio, need to set up gateway to forward to this port from 80
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
