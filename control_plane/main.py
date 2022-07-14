from fastapi import FastAPI
from routers import artifact

import os
import uvicorn

# We need a different root path when serving in cluster
app = FastAPI(root_path = os.environ.get("FAST_API_ROOT", "/"))

app.include_router(artifact.app)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)