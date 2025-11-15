from datetime import datetime, timezone, date
from database.models import Account 
from sqlalchemy.orm import Session
from sqlalchemy import and_, select,extract, insert
from typing import Dict


def set_account(session: Session, name:str) -> bool:
    """Crea un account"""
    try:
        stmt = insert(Account).values(
            name = name
        )

        session.execute(stmt)
        session.commit()
        return True
    except Exception as e:
        print(f"Errore nell'impostare il target: {e}")
        return False


def get_accounts(session: Session) -> Dict[str, float]:
    """Recupera tutti i target mensili"""
    stmt = select(Account)
    result = session.execute(stmt).scalars().all()
    return result

if __name__ == "__main__":

    from database.postgres_connection import init_postgres_db
    pg_engine, pg_session = init_postgres_db()

    get_accounts(pg_session)

