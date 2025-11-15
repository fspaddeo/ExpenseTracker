from datetime import datetime, timezone, date
from database.models import Income 
from sqlalchemy.orm import Session
from sqlalchemy import and_, select,extract, insert
from typing import Dict


def set_income(session: Session, amount: float, date: date, account_id: int) -> bool:
    """Imposta o aggiorna il target mensile per una categoria"""
    try:
        stmt = insert(Income).values(
            amount=amount,
            date=date,
            account_id=account_id
        )

        session.execute(stmt)
        session.commit()
        return True
    except Exception as e:
        print(f"Errore nell'impostare il target: {e}")
        return False


def get_income(session: Session, account_id: int, year:int, month: int) -> Dict[str, float]:
    """Recupera tutti i target mensili"""
    stmt = select(Income).where(and_(extract('year', Income.date) == year,
            extract('month', Income.date) == month), Income.account_id == account_id)
    result = session.execute(stmt).scalars().first()
    return result

if __name__ == "__main__":

    from database.postgres_connection import init_postgres_db
    pg_engine, pg_session = init_postgres_db()
    # set_income(pg_session, amount=1690, date=date(2025,11,10), account_id=1)
    get_income(pg_session, 1, 2025, 11)



