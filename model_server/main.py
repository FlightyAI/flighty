from typing import Union
from customer_code import main
from fastapi import FastAPI
from inspect import signature
from pydantic import BaseModel, create_model

import json
import uvicorn

app = FastAPI()

pred_sig = signature(main.predict)
parameters = pred_sig.parameters
user_type = {}
for k in parameters:
  user_type = parameters[k].annotation

@app.on_event("startup")
async def startup_event():
  main.init()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/infer")
def predict(input : user_type):
  main.predict(input)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
