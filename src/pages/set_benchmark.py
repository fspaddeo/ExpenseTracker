import streamlit as st
import pandas as pd
import plotly.express as px
from database.postgres_connection import init_postgres_db
from services.expense_service import CATEGORIES
from services.target_service import get_targets, set_target

pg_engine, pg_session = init_postgres_db()

st.header("Imposta Target Mensili per Categoria")
st.set_page_config(
    page_title="Imposta Target Mensili per Categoria", page_icon="💰", layout="wide"
)
st.title("Imposta Target Mensili per Categoria")

st.info(
    "💡 Imposta i limiti di spesa mensili che desideri rispettare per ogni categoria."
)

# Recupera i target esistenti
current_targets = get_targets(pg_session)

# Form per impostare i target
with st.form("targets_form"):
    st.subheader("Configura i Target")

    targets_data = {}

    # Crea due colonne per organizzare meglio i campi
    col1, col2 = st.columns(2)

    for i, category in enumerate(CATEGORIES):
        current_value = current_targets.get(category, 0.0)

        with col1 if i % 2 == 0 else col2:
            targets_data[category] = st.number_input(
                f"{category}",
                min_value=0.0,
                value=current_value,
                step=10.0,
                format="%.2f",
                key=f"target_{category}",
            )

    submitted = st.form_submit_button(
        "💾 Salva Tutti i Target", type="primary", use_container_width=True
    )

    if submitted:
        success_count = 0
        for category, target_amount in targets_data.items():
            if target_amount > 0:
                if set_target(pg_session, category, target_amount):
                    success_count += 1

        if success_count > 0:
            st.success(f"✅ {success_count} target salvati con successo!")
            st.rerun()
        else:
            st.warning("⚠️ Nessun target impostato (tutti i valori sono zero).")

# Mostra i target attuali
if current_targets:
    st.subheader("Target Attuali")

    targets_display = pd.DataFrame(
        [
            {"Categoria": cat, "Target Mensile": f"€{amount:.2f}"}
            for cat, amount in current_targets.items()
        ]
    )
    targets_display = targets_display.sort_values("Categoria")

    st.dataframe(targets_display, use_container_width=True, hide_index=True)

    # Grafico a barre dei target
    fig_targets = px.bar(
        pd.DataFrame(
            [
                {"Categoria": cat, "Target": amount}
                for cat, amount in current_targets.items()
            ]
        ).sort_values("Target", ascending=False),
        x="Categoria",
        y="Target",
        title="Visualizzazione Target Mensili",
    )
    st.plotly_chart(fig_targets, use_container_width=True)
