from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from .base import Base
import streamlit as st

conn_string = f"postgresql+psycopg2://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}@{st.secrets['DB_HOST']}/{st.secrets['DB_NAME']}?sslmode=require&channel_binding=require"

pg_engine = create_engine(conn_string)
PostgresSession = sessionmaker(bind=pg_engine)


def init_postgres_db() -> tuple[Engine, Session]:
    Base.metadata.create_all(pg_engine)
    return pg_engine, PostgresSession()
