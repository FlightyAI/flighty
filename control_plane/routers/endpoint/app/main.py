from fastapi import FastAPI
import json
from pydantic import BaseModel
import mysql.connector

class Endpoint(BaseModel):
    name: str
    prod_traffic: int = 0
    shadow_traffic: int = 0

app = FastAPI()
# TODO - factor this out into shared library across all services
try:   
    cnx = mysql.connector.connect(host="mysql.default.svc.cluster.local", password="password", database="flighty")
    print("using k8s service discovery")
except mysql.connector.errors.DatabaseError:
    try:
        # Attempt to connect to localhost if we are doing local development
        cnx = mysql.connector.connect(host="127.0.0.1", password="password", database="flighty")
        print("using 127.0.0.1")
    except mysql.connector.errors.DatabaseError:
        # if we're running in Docker
        cnx = mysql.connector.connect(host="host.docker.internal", password="password", database="flighty")
        print("using host Docker internal")
c=cnx.cursor(dictionary=True)

@app.get("/list")
def show_endpoints():
    c.execute("""SELECT * FROM endpoints""")
    return (json.dumps(c.fetchall()))

@app.post("/create")
async def create_endpoint(endpoint: Endpoint):
    try:
        c.execute("INSERT INTO endpoints (name) VALUES (%s)", (endpoint.name, ))
        cnx.commit()
        return endpoint
    except mysql.connector.errors.IntegrityError:
        return f"Endpoint with name {endpoint.name} already exists"

@app.post("/delete")
async def delete_endpoint(endpoint: Endpoint):
    #try:
    c.execute("DELETE FROM `endpoints` WHERE name = %s", (endpoint.name, ))
    cnx.commit()
    return f"Endpoint {endpoint.name} successfully deleted"
    # except mysql.connector.errors.IntegrityError:
    #     return f"Endpoint with name {endpoint.name} already exists"
    
@app.post("/update")
async def update_endpoint(endpoint: Endpoint):
    pass