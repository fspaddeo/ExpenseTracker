from abc import ABC, abstractmethod
from typing import Any
from sqlite3 import Connection
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional


class IExpenseDatabase(ABC):
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
        "Abbigliamento"
    ]
    @abstractmethod
    def get_connection(self) -> Connection:
        pass
    
    @abstractmethod
    def add_expense(self, date: str, category: str, amount: float, description: str) -> bool:
        pass
    
    @abstractmethod
    def update_expense(self, expense_id: int, date: str, category: str, amount: float, description: str) -> bool:
        pass
    
    @abstractmethod
    def delete_expense(self, expense_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict]:
        """Recupera una singola spesa per ID"""
        pass
    
    @abstractmethod
    def get_all_expenses(self) -> pd.DataFrame:
        """Recupera tutte le spese come DataFrame"""
        pass
    
    @abstractmethod
    def get_expenses_by_month(self, year: int, month: int) -> pd.DataFrame:
        """Recupera le spese per un mese specifico"""
        pass
    
    @abstractmethod
    def get_expenses_by_year(self, year: int) -> pd.DataFrame:
        """Recupera le spese per un anno specifico"""
        pass
    
    @abstractmethod
    def get_expenses_by_date_range(self, start_date, end_date) -> pd.DataFrame:
        """Recupera le spese per un range di date personalizzato"""
        pass
    
    @abstractmethod
    def import_expenses_from_dataframe(self, df: pd.DataFrame) -> tuple:
        """Importa spese da un DataFrame con validazione rigida delle categorie"""
        pass
    
    @abstractmethod
    def set_target(self, category: str, target_amount: float) -> bool:
        """Imposta o aggiorna il target mensile per una categoria"""
        pass
    
    @abstractmethod
    def get_targets(self) -> Dict[str, float]:
        """Recupera tutti i target mensili"""
        pass
    
    @abstractmethod
    def get_category_spending(self, year: int, month: int) -> pd.DataFrame:
        """Calcola la spesa totale per categoria in un mese specifico"""
        pass
    
    @abstractmethod
    def get_monthly_totals(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Calcola i totali mensili per periodo"""
        pass
    
    @abstractmethod
    def get_overall_monthly_totals(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Calcola i totali mensili complessivi per periodo"""
        pass

