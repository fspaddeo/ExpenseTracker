from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
import streamlit as st

sqlite_engine = create_engine(st.secrets["SQLITE_URL"])
SQLiteSession = sessionmaker(bind=sqlite_engine)


def init_sqlite_db():
    Base.metadata.create_all(sqlite_engine)
    return SQLiteSession()
