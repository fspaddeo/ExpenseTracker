import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from database.expense_database_base import IExpenseDatabase
import psycopg2
import streamlit as st
from sqlalchemy import create_engine, text

PLACEHOLDER = "%s"

class ExpenseDatabase(IExpenseDatabase):
    """Classe per gestire il database delle spese"""

    def get_connection(self):
        return super().get_connection()
    
    def get_engine(self):
        """Crea una connessione al database"""
        # conn = psycopg2.connect(
        #     host=st.secrets["DB_HOST"],
        #     user=st.secrets["DB_USER"],
        #     password=st.secrets["DB_PASS"],
        #     dbname=st.secrets["DB_NAME"],
        #     port=st.secrets.get("DB_PORT", "5432"),
        #     sslmode=st.secrets.get("DB_SSLMODE", "require"),
        #     channel_binding=st.secrets.get("DB_CHANNEL_BINDING", "require")
        # )
        conn_string = f"postgresql+psycopg2://{st.secrets['DB_USER']}:{st.secrets['DB_PASS']}@{st.secrets['DB_HOST']}/{st.secrets['DB_NAME']}?sslmode=require&channel_binding=require"
        engine = create_engine(conn_string)
        return engine
    

    def add_expense(self, date: str, category: str, amount: float, description: str) -> bool:
        """Aggiunge una nuova spesa al database"""
        try:
            # Validazione categoria
            if category not in self.CATEGORIES:
                print(f"Errore: categoria '{category}' non valida. Categorie ammesse: {', '.join(self.CATEGORIES)}")
                return False
            
            engine = self.get_engine()
            with engine.begin() as conn:
            
                conn.execute(text(f"""
                    INSERT INTO expenses (date, category, amount, description)
                    VALUES (:date, :category, :amount, :description)
                """), {"date":date, "category":category, "amount":amount, "description":description})
            
            return True
        except Exception as e:
            print(f"Errore nell'aggiungere la spesa: {e}")
            return False
    
    def update_expense(self, expense_id: int, date: str, category: str, amount: float, description: str) -> bool:
        """Aggiorna una spesa esistente"""
        try:
            # Validazione categoria
            if category not in self.CATEGORIES:
                print(f"Errore: categoria '{category}' non valida. Categorie ammesse: {', '.join(self.CATEGORIES)}")
                return False
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE expenses 
                SET date = {PLACEHOLDER}, category = {PLACEHOLDER}, amount = {PLACEHOLDER}, description = {PLACEHOLDER}
                WHERE id = {PLACEHOLDER}
            """, (date, category, amount, description, expense_id))
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            return rows_affected > 0
        except Exception as e:
            print(f"Errore nell'aggiornare la spesa: {e}")
            return False
    
    def delete_expense(self, expense_id: int) -> bool:
        """Elimina una spesa dal database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"DELETE FROM expenses WHERE id = {PLACEHOLDER}", (expense_id,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()
            
            return rows_affected > 0
        except Exception as e:
            print(f"Errore nell'eliminare la spesa: {e}")
            return False
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict]:
        """Recupera una singola spesa per ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM expenses WHERE id = {PLACEHOLDER}", (expense_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'date': row[1],
                    'category': row[2],
                    'amount': row[3],
                    'description': row[4],
                    'created_at': row[5]
                }
            return None
        except Exception as e:
            print(f"Errore nel recuperare la spesa: {e}")
            return None
    
    def get_all_expenses(self) -> pd.DataFrame:
        """Recupera tutte le spese come DataFrame"""
        engine = self.get_engine()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY date DESC", engine)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_expenses_by_month(self, year: int, month: int) -> pd.DataFrame:
        """Recupera le spese per un mese specifico"""
        conn = self.get_connection()
        
        # Crea il range di date per il mese
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        query = f"""
            SELECT * FROM expenses 
            WHERE date >= {PLACEHOLDER} AND date < {PLACEHOLDER}
            ORDER BY date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_expenses_by_year(self, year: int) -> pd.DataFrame:
        """Recupera le spese per un anno specifico"""
        conn = self.get_connection()
        
        start_date = f"{year}-01-01"
        end_date = f"{year+1}-01-01"
        
        query = f"""
            SELECT * FROM expenses 
            WHERE date >= {PLACEHOLDER} AND date < {PLACEHOLDER}
            ORDER BY date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_expenses_by_date_range(self, start_date, end_date) -> pd.DataFrame:
        """Recupera le spese per un range di date personalizzato"""
        conn = self.get_connection()
        
        # Converti le date in stringa se necessario
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%Y-%m-%d')
        else:
            start_str = str(start_date)
        
        if hasattr(end_date, 'strftime'):
            end_str = end_date.strftime('%Y-%m-%d')
        else:
            end_str = str(end_date)
        
        query = f"""
            SELECT * FROM expenses 
            WHERE date >= {PLACEHOLDER} AND date <= {PLACEHOLDER}
            ORDER BY date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(start_str, end_str))
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def import_expenses_from_dataframe(self, df: pd.DataFrame) -> tuple:
        """Importa spese da un DataFrame con validazione rigida delle categorie"""
        success_count = 0
        error_count = 0
        invalid_categories = []
        
        for idx, row in df.iterrows():
            try:
                # Converti la data in formato stringa se necessario
                if isinstance(row['date'], pd.Timestamp):
                    date_str = row['date'].strftime('%Y-%m-%d')
                else:
                    date_str = str(row['date'])
                
                # Validazione categoria prima dell'inserimento
                category = str(row['category'])
                if category not in self.CATEGORIES:
                    if category not in invalid_categories:
                        invalid_categories.append(category)
                    error_count += 1
                    continue
                
                if self.add_expense(
                    date=date_str,
                    category=category,
                    amount=float(row['amount']),
                    description=str(row['description'])
                ):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"Errore nell'importare riga {idx}: {e}")
                error_count += 1
        
        # Stampa le categorie non valide trovate
        if invalid_categories:
            print(f"Categorie non valide trovate: {', '.join(invalid_categories)}")
        
        return success_count, error_count
    
    def set_target(self, category: str, target_amount: float) -> bool:
        """Imposta o aggiorna il target mensile per una categoria"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                INSERT OR REPLACE INTO monthly_targets (category, target_amount, updated_at)
                VALUES ({PLACEHOLDER}, {PLACEHOLDER}, CURRENT_TIMESTAMP)
            """, (category, target_amount))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Errore nell'impostare il target: {e}")
            return False
    
    def get_targets(self) -> Dict[str, float]:
        """Recupera tutti i target mensili"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, target_amount FROM monthly_targets")
        targets = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return targets
    
    def get_category_spending(self, year: int, month: int) -> pd.DataFrame:
        """Calcola la spesa totale per categoria in un mese specifico"""
        df = self.get_expenses_by_month(year, month)
        
        if df.empty:
            # Ritorna un DataFrame vuoto con le colonne corrette
            return pd.DataFrame(columns=['category', 'total'])
        
        category_totals = df.groupby('category')['amount'].sum().reset_index()
        category_totals.columns = ['category', 'total']
        
        return category_totals
    
    def get_monthly_totals(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Calcola i totali mensili per periodo"""
        conn = self.get_connection()
        
        query = f"""
            SELECT 
                strftime('%Y-%m', date) as month,
                category,
                SUM(amount) as total
            FROM expenses
            WHERE date >= {PLACEHOLDER} AND date <= {PLACEHOLDER}
            GROUP BY month, category
            ORDER BY month
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        return df
    
    def get_overall_monthly_totals(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Calcola i totali mensili complessivi per periodo"""
        conn = self.get_connection()
        
        query = f"""
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(amount) as total
            FROM expenses
            WHERE date >= {PLACEHOLDER} AND date <= {PLACEHOLDER}
            GROUP BY month
            ORDER BY month
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        return df

# if __name__ == "__main__":
db = ExpenseDatabase()
    # db.get_connection()

