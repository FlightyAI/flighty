import mysql.connector

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# HACK - automatically discover whether we're on localhost or not
db_conn_info = {
    "user": "root",
    "password": "password",
    "host": "mysql.default.svc.cluster.local",
    "database": "flighty"
}

try:   
    cnx = mysql.connector.connect(**db_conn_info)
except mysql.connector.errors.DatabaseError:
    try:
        # Attempt to connect to localhost if we are doing local development
        db_conn_info['host'] = '127.0.0.1'
        cnx = mysql.connector.connect(**db_conn_info)
        
    except mysql.connector.errors.DatabaseError:
        # if we're running in Docker
        db_conn_info['host'] = 'host.docker.internal'
        cnx = mysql.connector.connect(**db_conn_info)
finally:
    cnx.close()

SQLALCHEMY_DATABASE_URL = (f"mysql://{db_conn_info['user']}:{db_conn_info['password']}"
  f"@{db_conn_info['host']}/{db_conn_info['database']}")
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL#, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()