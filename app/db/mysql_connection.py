import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime

load_dotenv()  # MUST be called before os.getenv()

# MySQL connection using SQLMODEL

DB_URL = os.getenv("MYSQL_DB_URL")

engine = create_engine(DB_URL, echo=True, connect_args={"ssl": {"require": True}})   # echo = True --> shows logs / queries in the console

# SESSION DEPENDENCY (CONTROLLED DB ACCESS)

def get_session():
    with Session(engine) as session:
        yield session

