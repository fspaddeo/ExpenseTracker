from datetime import datetime, timezone
from database.models import MonthlyTarget
from sqlalchemy.orm import Session
from typing import Dict

def set_target(session:Session, category: str, target_amount: float) -> bool:
    """Imposta o aggiorna il target mensile per una categoria"""
    try:
        target = MonthlyTarget(
            category=category,
            target_amount=target_amount,
            updated_at=datetime.now(timezone.utc)
        )
        session.merge(target)  # merge inserisce se non esiste, altrimenti aggiorna
        session.commit()
        return True
    except Exception as e:
        print(f"Errore nell'impostare il target: {e}")
        return False

def get_targets(session:Session) -> Dict[str, float]:
    """Recupera tutti i target mensili"""
    results = session.query(MonthlyTarget.category, MonthlyTarget.target_amount).all()
    targets = {category: amount for category, amount in results}
    return targets






