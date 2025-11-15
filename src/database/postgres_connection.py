from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from .base import Base
import streamlit as st
import os
from streamlit.runtime.secrets import StreamlitSecretNotFoundError

try:
    db_user = st.secrets["postgres"]["DB_USER"]
    db_pass = st.secrets["postgres"]["DB_PASS"]
    db_host = st.secrets["postgres"]["DB_HOST"]
    db_name = st.secrets["postgres"]["DB_NAME"]
except StreamlitSecretNotFoundError:
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")


conn_string = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}?sslmode=require&channel_binding=require"

pg_engine = create_engine(conn_string)
PostgresSession = sessionmaker(bind=pg_engine)


def init_postgres_db() -> tuple[Engine, Session]:
    Base.metadata.create_all(pg_engine)
    return pg_engine, PostgresSession()
