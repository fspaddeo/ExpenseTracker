import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io
from database import neon_db as db

from enum import Enum


st.header("Importa ed Esporta Dati")
st.set_page_config(page_title="Importa ed Esporta Dati",
    page_icon="💰",
    layout="wide"
)
st.title("Importa ed Esporta Dati")

# Sezione Esportazione
st.subheader("📤 Esporta le Tue Spese")

all_expenses_export = db.get_all_expenses()

if not all_expenses_export.empty:
    # Prepara i dati per l'esportazione
    export_df = all_expenses_export.copy()
    export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
    export_df = export_df[['date', 'category', 'amount', 'description']]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Totale Spese", len(export_df))
    with col2:
        st.metric("Importo Totale", f"€{export_df['amount'].sum():.2f}")
    with col3:
        st.metric(
            "Periodo",
            f"{export_df['date'].min()} - {export_df['date'].max()}")

    col1, col2 = st.columns(2)

    with col1:
        # Download CSV
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica CSV",
            data=csv_data,
            file_name=
            f"spese_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary")

    with col2:
        # Download Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Spese')
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Scarica Excel",
            data=excel_data,
            file_name=
            f"spese_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary")
else:
    st.info(
        "Nessuna spesa da esportare. Aggiungi delle spese prima di procedere con l'esportazione."
    )

# Sezione Importazione
st.divider()
st.subheader("📥 Importa Spese da File")

st.info("""
📋 **Formato richiesto per il file:**
- Colonne necessarie: `date`, `category`, `amount`, `description`
- Formato data: YYYY-MM-DD (es. 2025-01-15)
- Categorie devono corrispondere a quelle disponibili nell'app
- Formati supportati: CSV, Excel (.xlsx, .xls)
""")

# Mostra esempio di formato
with st.expander("📄 Visualizza esempio di formato corretto"):
    example_data = pd.DataFrame({
        'date': ['2025-01-15', '2025-01-20', '2025-02-05'],
        'category': ['Alimentari', 'Spese auto', 'Svago'],
        'amount': [50.25, 60.00, 35.80],
        'description':
        ['Spesa settimanale', 'Rifornimento auto', 'Cena con amici']
    })
    st.dataframe(example_data, use_container_width=True, hide_index=True)

# Mostra le categorie valide
with st.expander("📋 Lista categorie valide"):
    st.write(", ".join(db.CATEGORIES))

# Upload file
uploaded_file = st.file_uploader(
    "Carica il file con le spese",
    type=['csv', 'xlsx', 'xls'],
    help="Carica un file CSV o Excel con le tue spese")

if uploaded_file is not None:
    try:
        # Leggi il file in base al tipo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Anteprima Dati")
        st.dataframe(df.head(10), use_container_width=True)

        # Validazione delle colonne
        required_columns = ['date', 'category', 'amount', 'description']
        validation_errors = []
        missing_columns = [
            col for col in required_columns if col not in df.columns
        ]
        if missing_columns:
            validation_errors.append(f"❌ Colonne mancanti nel file: {', '.join(missing_columns)}")
        # Validazione date
        if not validation_errors:
            try:
                for idx,row in df.iterrows():
                    row["date"] = datetime.strptime(row["date"], "%Y-%m-%d").date().isoformat()
            except Exception:
                validation_errors.append(f"❌ Row {idx} has invalid date format: {row['date']}")

        if validation_errors:
            for err in validation_errors:
                st.error(
                    err
                )
        else:
            # Validazione categorie
            invalid_categories = df[~df['category'].isin(db.CATEGORIES)][
                'category'].unique()

            if len(invalid_categories) > 0:
                st.warning(
                    f"⚠️ Attenzione: alcune categorie non sono valide: {', '.join(invalid_categories)}"
                )
                st.write("Categorie valide:", ", ".join(db.CATEGORIES))
            
            

            # Mostra statistiche
            col1, col2, col3 = st.columns(3)
            col1.metric("Righe Totali", len(df))
            col2.metric("Importo Totale", f"€{df['amount'].sum():.2f}")
            col3.metric("Periodo",
                        f"{df['date'].min()} - {df['date'].max()}")

            # Pulsante per importare
            if st.button("📥 Importa Spese",
                            type="primary",
                            use_container_width=True):
                with st.spinner("Importazione in corso..."):
                    success_count, error_count = db.import_expenses_from_dataframe(
                        df)

                if success_count > 0:
                    st.success(
                        f"✅ {success_count} spese importate con successo!")
                    if error_count > 0:
                        st.warning(
                            f"⚠️ {error_count} righe non importate a causa di errori."
                        )
                    st.balloons()
                else:
                    st.error(
                        "❌ Errore nell'importazione. Verifica il formato del file."
                    )

    except Exception as e:
        st.error(f"❌ Errore nella lettura del file: {str(e)}")
        st.info("Assicurati che il file sia nel formato corretto.")
