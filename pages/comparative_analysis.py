import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io
from database import db
from enum import Enum
from models import format_month_year, MESI_ITALIANI

st.header("Analisi Comparative tra Periodi")
st.set_page_config(page_title="Analisi Comparative tra Periodi",
    page_icon="💰",
    layout="wide"
)
st.title("Analisi Comparative tra Periodi")

st.info(
    "💡 Confronta le tue spese tra due periodi diversi per identificare cambiamenti e tendenze."
)

# Selezione tipo di confronto
comparison_type = st.radio(
    "Tipo di confronto:",
    ["Mese vs Mese", "Anno vs Anno", "Periodo Personalizzato"],
    horizontal=True)

if comparison_type == "Mese vs Mese":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Periodo 1")
        year1 = st.selectbox("Anno",
                                options=list(
                                    range(datetime.now().year,
                                        datetime.now().year - 10, -1)),
                                index=0,
                                key="year1")
        month1 = st.selectbox("Mese",
                                options=list(range(1, 13)),
                                format_func=lambda x: MESI_ITALIANI[x],
                                index=datetime.now().month -
                                2 if datetime.now().month > 1 else 11,
                                key="month1")

    with col2:
        st.subheader("Periodo 2")
        year2 = st.selectbox("Anno",
                                options=list(
                                    range(datetime.now().year,
                                        datetime.now().year - 10, -1)),
                                index=0,
                                key="year2")
        month2 = st.selectbox("Mese",
                                options=list(range(1, 13)),
                                format_func=lambda x: MESI_ITALIANI[x],
                                index=datetime.now().month - 1,
                                key="month2")

    # Recupera i dati per entrambi i periodi
    expenses1 = db.get_expenses_by_month(year1, month1)
    expenses2 = db.get_expenses_by_month(year2, month2)
    category_spending1 = db.get_category_spending(year1, month1)
    category_spending2 = db.get_category_spending(year2, month2)

    period1_label = format_month_year(year1, month1)
    period2_label = format_month_year(year2, month2)

elif comparison_type == "Anno vs Anno":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Anno 1")
        year1 = st.selectbox("Seleziona anno",
                                options=list(
                                    range(datetime.now().year,
                                        datetime.now().year - 10, -1)),
                                index=1,
                                key="year1_full")

    with col2:
        st.subheader("Anno 2")
        year2 = st.selectbox("Seleziona anno",
                                options=list(
                                    range(datetime.now().year,
                                        datetime.now().year - 10, -1)),
                                index=0,
                                key="year2_full")

    # Recupera i dati per entrambi gli anni
    expenses1 = db.get_expenses_by_year(year1)
    expenses2 = db.get_expenses_by_year(year2)

    # Calcola totali per categoria
    if not expenses1.empty:
        category_spending1 = expenses1.groupby(
            'category')['amount'].sum().reset_index()
        category_spending1.columns = ['category', 'total']
    else:
        category_spending1 = pd.DataFrame(columns=['category', 'total'])

    if not expenses2.empty:
        category_spending2 = expenses2.groupby(
            'category')['amount'].sum().reset_index()
        category_spending2.columns = ['category', 'total']
    else:
        category_spending2 = pd.DataFrame(columns=['category', 'total'])

    period1_label = str(year1)
    period2_label = str(year2)

else:  # Periodo Personalizzato
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Periodo 1")
        start1 = st.date_input("Data inizio",
                                value=date.today() -
                                relativedelta(months=2),
                                key="start1",
                                format="YYYY-MM-DD")
        end1 = st.date_input("Data fine",
                                value=date.today() - relativedelta(months=1),
                                key="end1",
                                format="YYYY-MM-DD")

    with col2:
        st.subheader("Periodo 2")
        start2 = st.date_input("Data inizio",
                                value=date.today() -
                                relativedelta(months=1),
                                key="start2",
                                format="YYYY-MM-DD")
        end2 = st.date_input("Data fine",
                                value=date.today(),
                                key="end2",
                                format="YYYY-MM-DD")

    # Recupera i dati per i periodi personalizzati
    expenses1 = db.get_expenses_by_date_range(start1, end1)
    expenses2 = db.get_expenses_by_date_range(start2, end2)

    # Calcola totali per categoria
    if not expenses1.empty:
        category_spending1 = expenses1.groupby(
            'category')['amount'].sum().reset_index()
        category_spending1.columns = ['category', 'total']
    else:
        category_spending1 = pd.DataFrame(columns=['category', 'total'])

    if not expenses2.empty:
        category_spending2 = expenses2.groupby(
            'category')['amount'].sum().reset_index()
        category_spending2.columns = ['category', 'total']
    else:
        category_spending2 = pd.DataFrame(columns=['category', 'total'])

    period1_label = f"{start1.strftime('%d/%m/%Y')} - {end1.strftime('%d/%m/%Y')}"
    period2_label = f"{start2.strftime('%d/%m/%Y')} - {end2.strftime('%d/%m/%Y')}"

# Mostra confronto solo se entrambi i periodi hanno dati
if not expenses1.empty or not expenses2.empty:
    st.subheader(f"📊 Confronto: {period1_label} vs {period2_label}")

    # Calcola statistiche generali
    total1 = expenses1['amount'].sum() if not expenses1.empty else 0
    total2 = expenses2['amount'].sum() if not expenses2.empty else 0
    count1 = len(expenses1) if not expenses1.empty else 0
    count2 = len(expenses2) if not expenses2.empty else 0
    avg1 = total1 / count1 if count1 > 0 else 0
    avg2 = total2 / count2 if count2 > 0 else 0

    # Delta calcoli
    total_delta = total2 - total1
    total_delta_pct = ((total2 - total1) / total1 *
                        100) if total1 > 0 else 0
    count_delta = count2 - count1
    avg_delta = avg2 - avg1

    # Metriche principali
    col1, col2, col3 = st.columns(3)

    col1.metric("Totale Speso",
                f"€{total2:.2f}",
                delta=f"€{total_delta:+.2f} ({total_delta_pct:+.1f}%)",
                delta_color="inverse")
    col2.metric("Numero Transazioni",
                count2,
                delta=f"{count_delta:+d}",
                delta_color="off")
    col3.metric("Media per Transazione",
                f"€{avg2:.2f}",
                delta=f"€{avg_delta:+.2f}",
                delta_color="inverse")

    # Confronto per categoria
    st.subheader("Confronto per Categoria")

    # Prepara dati per il confronto
    comparison_data = []
    for category in db.CATEGORIES:
        spent1 = category_spending1[category_spending1['category'] ==
                                    category]['total'].sum()
        spent2 = category_spending2[category_spending2['category'] ==
                                    category]['total'].sum()

        if spent1 > 0 or spent2 > 0:
            delta = spent2 - spent1
            delta_pct = ((spent2 - spent1) / spent1 *
                            100) if spent1 > 0 else (100 if spent2 > 0 else 0)

            comparison_data.append({
                'Categoria': category,
                period1_label: f"€{spent1:.2f}",
                period2_label: f"€{spent2:.2f}",
                'Differenza': f"€{delta:+.2f}",
                'Variazione %': f"{delta_pct:+.1f}%"
            })

    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison,
                        use_container_width=True,
                        hide_index=True)

        # Grafico a barre comparativo
        chart_data = []
        for category in db.CATEGORIES:
            spent1 = category_spending1[category_spending1['category'] ==
                                        category]['total'].sum()
            spent2 = category_spending2[category_spending2['category'] ==
                                        category]['total'].sum()

            if spent1 > 0 or spent2 > 0:
                chart_data.append({
                    'Categoria': category,
                    period1_label: spent1,
                    period2_label: spent2
                })

        if chart_data:
            df_chart = pd.DataFrame(chart_data)

            fig_comparison = go.Figure(data=[
                go.Bar(name=period1_label,
                        x=df_chart['Categoria'],
                        y=df_chart[period1_label],
                        marker_color='lightblue'),
                go.Bar(name=period2_label,
                        x=df_chart['Categoria'],
                        y=df_chart[period2_label],
                        marker_color='lightcoral')
            ])
            fig_comparison.update_layout(
                barmode='group',
                title=
                f"Confronto Spese per Categoria: {period1_label} vs {period2_label}",
                xaxis_title="Categoria",
                yaxis_title="Importo (€)")
            st.plotly_chart(fig_comparison, use_container_width=True)

            # Grafico variazione percentuale
            st.subheader("Variazioni Percentuali per Categoria")

            variation_data = []
            for category in db.CATEGORIES:
                spent1 = category_spending1[category_spending1['category']
                                            == category]['total'].sum()
                spent2 = category_spending2[category_spending2['category']
                                            == category]['total'].sum()

                if spent1 > 0:
                    delta_pct = ((spent2 - spent1) / spent1 * 100)
                    variation_data.append({
                        'Categoria': category,
                        'Variazione %': delta_pct
                    })

            if variation_data:
                df_variation = pd.DataFrame(variation_data).sort_values(
                    'Variazione %', ascending=True)

                fig_variation = px.bar(
                    df_variation,
                    x='Variazione %',
                    y='Categoria',
                    orientation='h',
                    title=
                    "Variazione Percentuale delle Spese per Categoria",
                    color='Variazione %',
                    color_continuous_scale=['green', 'yellow', 'red'],
                    color_continuous_midpoint=0)
                st.plotly_chart(fig_variation, use_container_width=True)
    else:
        st.info(
            "Nessuna spesa da confrontare per le categorie selezionate.")
else:
    st.warning("⚠️ Nessun dato disponibile per i periodi selezionati.")
