import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io
from database import neon_db as db
from enum import Enum

st.header("Inserisci una Nuova Spesa")
st.set_page_config(page_title="Gestione Spese Personali",
    page_icon="💰",
    layout="wide"
)
st.title("Inserisci una Nuova Spesa")

col1, col2 = st.columns(2)

with col1:
    expense_date = st.date_input("Data",
                                    value=date.today(),
                                    format="YYYY-MM-DD")

    category = st.selectbox("Categoria", options=db.CATEGORIES)

    amount = st.number_input("Importo (€)",
                                min_value=0.0,
                                step=0.01,
                                format="%.2f")

with col2:
    description = st.text_area(
        "Descrizione *",
        height=150,
        placeholder="Inserisci una descrizione della spesa...")

if st.button("💾 Salva Spesa", type="primary", use_container_width=True):
    if not expense_date:
        st.error("⚠️ La data è obbligatoria!")
    elif not category:
        st.error("⚠️ La categoria è obbligatoria!")
    elif amount <= 0:
        st.error("⚠️ L'importo deve essere maggiore di zero!")
    else:
        success = db.add_expense(date=expense_date.strftime('%Y-%m-%d'),
                                    category=category,
                                    amount=amount,
                                    description=description)

        if success:
            st.success(
                f"✅ Spesa di €{amount:.2f} per '{category}' salvata con successo!"
            )
            st.balloons()
        else:
            st.error("❌ Errore nel salvare la spesa. Riprova.")

# Gestione spese esistenti
st.divider()
st.subheader("✏️ Gestisci Spese Esistenti")

all_expenses = db.get_all_expenses()

if not all_expenses.empty:
    # Filtri
    col1, col2 = st.columns([2, 1])
    with col1:
        filter_category = st.multiselect("Filtra per categoria",
                                            options=["Tutte"] + db.CATEGORIES,
                                            default=["Tutte"])
    with col2:
        num_to_show = st.selectbox("Numero di spese da mostrare",
                                    options=[10, 25, 50, 100, "Tutte"],
                                    index=0)

    # Applica filtri
    filtered_expenses = all_expenses.copy()
    if "Tutte" not in filter_category and filter_category:
        filtered_expenses = filtered_expenses[
            filtered_expenses['category'].isin(filter_category)]

    if num_to_show != "Tutte":
        filtered_expenses = filtered_expenses.head(num_to_show)

    # Mostra tabella
    st.write(f"**{len(filtered_expenses)}** spese trovate")

    # Crea una tabella con azioni
    for idx, row in filtered_expenses.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns(
                [1.5, 1.5, 1, 2, 0.8, 0.8])

            with col1:
                st.write(f"📅 {row['date'].strftime('%d/%m/%Y')}")
            with col2:
                st.write(f"🏷️ {row['category']}")
            with col3:
                st.write(f"💰 €{row['amount']:.2f}")
            with col4:
                st.write(
                    f"📝 {row['description'][:50]}{'...' if len(row['description']) > 50 else ''}"
                )
            with col5:
                edit_key = f"edit_{row['id']}"
                if st.button("✏️", key=edit_key, help="Modifica"):
                    st.session_state['editing_expense_id'] = row['id']
                    st.rerun()
            with col6:
                delete_key = f"delete_{row['id']}"
                if st.button("🗑️",
                                key=delete_key,
                                help="Elimina",
                                type="secondary"):
                    st.session_state['deleting_expense_id'] = row['id']
                    st.rerun()

    # Dialogo di modifica
    if 'editing_expense_id' in st.session_state:
        expense_id = st.session_state['editing_expense_id']
        expense = db.get_expense_by_id(expense_id)

        if expense:
            st.divider()
            st.subheader(f"✏️ Modifica Spesa #{expense_id}")

            # Inizializza i valori in session_state se non esistono
            if f'edit_date_{expense_id}' not in st.session_state:
                st.session_state[
                    f'edit_date_{expense_id}'] = datetime.strptime(
                        expense['date'], '%Y-%m-%d').date()
                st.session_state[f'edit_category_{expense_id}'] = expense[
                    'category']
                st.session_state[f'edit_amount_{expense_id}'] = float(
                    expense['amount'])
                st.session_state[
                    f'edit_description_{expense_id}'] = expense[
                        'description']

            col1, col2 = st.columns(2)

            with col1:
                edit_date = st.date_input(
                    "Data",
                    value=st.session_state[f'edit_date_{expense_id}'],
                    format="YYYY-MM-DD",
                    key=f"date_input_{expense_id}")
                st.session_state[f'edit_date_{expense_id}'] = edit_date

                edit_category = st.selectbox(
                    "Categoria",
                    options=db.CATEGORIES,
                    index=db.CATEGORIES.index(
                        st.session_state[f'edit_category_{expense_id}'])
                    if st.session_state[f'edit_category_{expense_id}']
                    in db.CATEGORIES else 0,
                    key=f"category_input_{expense_id}")
                st.session_state[
                    f'edit_category_{expense_id}'] = edit_category

                edit_amount = st.number_input(
                    "Importo (€)",
                    min_value=0.01,
                    value=st.session_state[f'edit_amount_{expense_id}'],
                    step=0.01,
                    format="%.2f",
                    key=f"amount_input_{expense_id}")
                st.session_state[f'edit_amount_{expense_id}'] = edit_amount

            with col2:
                edit_description = st.text_area(
                    "Descrizione *",
                    value=st.
                    session_state[f'edit_description_{expense_id}'],
                    height=150,
                    key=f"description_input_{expense_id}")
                st.session_state[
                    f'edit_description_{expense_id}'] = edit_description

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salva Modifiche",
                                type="primary",
                                use_container_width=True,
                                key=f"save_btn_{expense_id}"):
                    if not st.session_state[
                            f'edit_description_{expense_id}'] or st.session_state[
                                f'edit_description_{expense_id}'].strip(
                                ) == "":
                        st.error("⚠️ La descrizione è obbligatoria!")
                    elif st.session_state[
                            f'edit_amount_{expense_id}'] <= 0:
                        st.error(
                            "⚠️ L'importo deve essere maggiore di zero!")
                    else:
                        success = db.update_expense(
                            expense_id=expense_id,
                            date=st.
                            session_state[f'edit_date_{expense_id}'].
                            strftime('%Y-%m-%d'),
                            category=st.
                            session_state[f'edit_category_{expense_id}'],
                            amount=st.
                            session_state[f'edit_amount_{expense_id}'],
                            description=st.session_state[
                                f'edit_description_{expense_id}'])

                        if success:
                            st.success("✅ Spesa aggiornata con successo!")
                            # Pulizia session state
                            for key in [
                                    f'edit_date_{expense_id}',
                                    f'edit_category_{expense_id}',
                                    f'edit_amount_{expense_id}',
                                    f'edit_description_{expense_id}'
                            ]:
                                if key in st.session_state:
                                    del st.session_state[key]
                            del st.session_state['editing_expense_id']
                            st.rerun()
                        else:
                            st.error(
                                "❌ Errore nell'aggiornare la spesa. Riprova."
                            )
            with col2:
                if st.button("❌ Annulla",
                                use_container_width=True,
                                key=f"cancel_btn_{expense_id}"):
                    # Pulizia session state
                    for key in [
                            f'edit_date_{expense_id}',
                            f'edit_category_{expense_id}',
                            f'edit_amount_{expense_id}',
                            f'edit_description_{expense_id}'
                    ]:
                        if key in st.session_state:
                            del st.session_state[key]
                    del st.session_state['editing_expense_id']
                    st.rerun()

    # Dialogo di conferma eliminazione
    if 'deleting_expense_id' in st.session_state:
        expense_id = st.session_state['deleting_expense_id']
        expense = db.get_expense_by_id(expense_id)

        if expense:
            st.divider()
            st.warning(
                f"⚠️ **Sei sicuro di voler eliminare questa spesa?**")
            st.write(f"**Data:** {expense['date']}")
            st.write(f"**Categoria:** {expense['category']}")
            st.write(f"**Importo:** €{expense['amount']:.2f}")
            st.write(f"**Descrizione:** {expense['description']}")

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🗑️ Sì, Elimina",
                                type="primary",
                                use_container_width=True):
                    if db.delete_expense(expense_id):
                        st.success("✅ Spesa eliminata con successo!")
                        del st.session_state['deleting_expense_id']
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'eliminare la spesa.")
            with col2:
                if st.button("❌ Annulla", use_container_width=True):
                    del st.session_state['deleting_expense_id']
                    st.rerun()
else:
    st.info("Nessuna spesa registrata ancora.")
