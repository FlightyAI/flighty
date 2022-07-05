from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/live")
def is_alive():
    return {"Hello": "World"}

@app.get("/ready")
def is_ready():
    return {"Hello": "World"}

@app.post("/items/{item_id}")
def infer(item_id: int):
    return {"item_id": item_id}
