from typing import Union
from customer_code import main
from fastapi import Depends, FastAPI
from inspect import signature
from pydantic import BaseModel, create_model

import json
import uvicorn

app = FastAPI()

sig = signature(main.predict)

query_params = {}
for k in sig.parameters:
  query_params[k] = (sig.parameters[k].annotation, ...)

query_model = create_model("Query", **query_params) # This is subclass of pydantic BaseModel

@app.on_event("startup")
async def startup_event():
    main.init()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/infer")
def predict(params: query_model = Depends()):
  p_as_dict = params.dict()
  return main.predict(**p_as_dict)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
