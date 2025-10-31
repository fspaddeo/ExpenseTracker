from datetime import date
from database.models import Expense
from sqlalchemy.orm import Session
from sqlalchemy import Engine
from typing import Optional, Dict, Any
import pandas as pd
from sqlalchemy import select, insert, func
from numpy import nan

CATEGORIES = [
    "Mutuo",
    "Casa",
    "Investimenti",
    "Spese auto",
    "Svago",
    "Alimentari",
    "Viaggi",
    "Regali",
    "Salute",
    "Cane",
    "Parrucchiere",
    "Mensa",
    "Telefono",
    "Donazione",
    "Caffè",
    "Abbigliamento",
]

MESI_ITALIANI = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}


def format_month_year(year: int, month: int) -> str:
    """Formatta mese e anno in italiano"""
    return f"{MESI_ITALIANI[month]} {year}"


def add_expense(
    session: Session, date: str, category: str, amount: float, description: str
) -> bool:
    try:
        # Validazione categoria
        if category not in CATEGORIES:
            print(
                f"Errore: categoria '{category}' non valida. Categorie ammesse: {', '.join(CATEGORIES)}"
            )
            return False

        expense = Expense(
            date=date, category=category, amount=amount, description=description
        )
        session.add(expense)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Errore nell'aggiungere la spesa: {e}")
        return False


def update_expense(
    session: Session,
    expense_id: int,
    date: str,
    category: str,
    amount: float,
    description: str,
) -> bool:
    try:
        if category not in CATEGORIES:
            print(
                f"Errore: categoria '{category}' non valida. Categorie ammesse: {', '.join(CATEGORIES)}"
            )
            return False
        rows_affected = (
            session.query(Expense)
            .filter(Expense.id == expense_id)
            .update(
                {
                    Expense.date: date,
                    Expense.category: category,
                    Expense.amount: amount,
                    Expense.description: description,
                }
            )
        )
        session.commit()
        return rows_affected > 0

    except Exception as e:
        session.rollback()
        print(f"Errore durante update_expense: {e}")
        return False


def delete_expense(session: Session, expense_id: int) -> bool:
    """Elimina una spesa dal database"""
    try:
        rows_affected = session.query(Expense).filter(Expense.id == expense_id).delete()
        session.commit()

        return rows_affected > 0
    except Exception as e:
        print(f"Errore nell'eliminare la spesa: {e}")
        return False


def get_expense_by_id(session: Session, expense_id: int) -> Optional[Dict[str, Any]]:
    """Recupera una singola spesa per ID"""
    try:
        expense = session.get(Expense, expense_id)
        if not expense:
            print(f"Nessuna spesa trovata con id={expense_id}")
            return None

        return expense.to_dict()
    except Exception as e:
        print(f"Errore nel recuperare la spesa: {e}")
        return None


def get_all_expenses(engine: Engine) -> pd.DataFrame:
    """Recupera tutte le spese come DataFrame"""
    stmt = select(Expense).order_by(Expense.date.desc())
    df = pd.read_sql(stmt, con=engine)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def get_expenses_by_month(engine: Engine, year: int, month: int) -> pd.DataFrame:
    """Recupera le spese per un mese specifico"""
    # Crea il range di date per il mese
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    stmt = (
        select(Expense)
        .where(Expense.date >= start_date, Expense.date < end_date)
        .order_by(Expense.date.desc())
    )

    df = pd.read_sql(stmt, con=engine)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def get_expenses_by_year(engine: Engine, year: int) -> pd.DataFrame:
    """Recupera le spese per un anno specifico"""

    start_date = f"{year}-01-01"
    end_date = f"{year + 1}-01-01"

    stmt = (
        select(Expense)
        .where(Expense.date >= start_date, Expense.date < end_date)
        .order_by(Expense.date.desc())
    )

    df = pd.read_sql(stmt, con=engine)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def get_expenses_by_date_range(
    engine: Engine, start_date: date, end_date: date
) -> pd.DataFrame:
    """Recupera le spese per un range di date personalizzato"""

    stmt = (
        select(Expense)
        .where(Expense.date >= start_date, Expense.date < end_date)
        .order_by(Expense.date.desc())
    )

    df = pd.read_sql(stmt, con=engine)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    return df


def import_expenses_from_dataframe(session: Session, df: pd.DataFrame) -> int:
    """Importa spese da un DataFrame con validazione rigida delle categorie"""
    invalid_categories = set(
        [
            row["category"]
            for _, row in df.iterrows()
            if row["category"] not in CATEGORIES
        ]
    )
    if invalid_categories:
        raise Exception(
            f"Trovate le seguenti categorie non valide: {invalid_categories}"
        )

    stmt = insert(Expense)
    df = df.replace({nan: None})
    data = df.to_dict(orient="records")
    session.execute(stmt, data)  #type: ignore
    session.commit()

    return len(df)


def get_category_spending(engine: Engine, year: int, month: int) -> pd.DataFrame:
    """Calcola la spesa totale per categoria in un mese specifico"""
    df = get_expenses_by_month(engine, year, month)

    if df.empty:
        # Ritorna un DataFrame vuoto con le colonne corrette
        return pd.DataFrame(columns=["category", "total"])

    category_totals = df.groupby("category")["amount"].sum().reset_index()
    category_totals.columns = ["category", "total"]

    return category_totals


def get_monthly_totals(session: Session, start_date, end_date, dialect="postgresql"):
    if dialect == "postgresql":
        month_expr = func.to_char(Expense.date, "YYYY-MM")
    else:
        month_expr = func.strftime("%Y-%m", Expense.date)

    stmt = (
        select(
            month_expr.label("month"),
            Expense.category,
            func.sum(Expense.amount).label("total"),
        )
        .where(Expense.date >= start_date, Expense.date <= end_date)
        .group_by("month", Expense.category)
        .order_by("month")
    )

    df = pd.DataFrame(session.execute(stmt).mappings().all())
    return df


def get_overall_monthly_totals(
    session: Session, start_date, end_date, dialect="postgresql"
):
    if dialect == "postgresql":
        month_expr = func.to_char(Expense.date, "YYYY-MM")
    else:
        month_expr = func.strftime("%Y-%m", Expense.date)

    stmt = (
        select(
            month_expr.label("month"),
            Expense.category,
            func.sum(Expense.amount).label("total"),
        )
        .where(Expense.date >= start_date, Expense.date <= end_date)
        .group_by("month")
        .order_by("month")
    )

    df = pd.DataFrame(session.execute(stmt).mappings().all())
    return df
