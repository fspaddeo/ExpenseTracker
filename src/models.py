from enum import Enum


class AppPages(Enum):
    CreateExpense = "📝 Inserisci Spesa"
    MonthlyDashboard = "📊 Dashboard Mensile"
    TimeTrend = "📈 Andamento Temporale"
    ComparativeAnalysis = "🔄 Analisi Comparative"
    SetBenchmark = "🎯 Imposta Target"
    ImportData = "📥 Importa Dati"


# Dizionario per la traduzione dei mesi in italiano
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
