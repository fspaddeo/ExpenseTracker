import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from models import MESI_ITALIANI, format_month_year
from database.postgres_connection import init_postgres_db
from services.expense_service import (
    CATEGORIES,
    get_expenses_by_month,
    get_category_spending,
)
from services.target_service import get_targets

pg_engine, pg_session = init_postgres_db()
st.header("Dashboard Mensile")
st.set_page_config(page_title="Dashboard Mensile", page_icon="💰", layout="wide")
st.title("Dashboard Mensile")

# Selettori per mese e anno
col1, col2 = st.columns(2)

with col1:
    selected_year = st.selectbox(
        "Anno",
        options=list(range(datetime.now().year, datetime.now().year - 10, -1)),
        index=0,
    )

with col2:
    selected_month = st.selectbox(
        "Mese",
        options=list(range(1, 13)),
        format_func=lambda x: MESI_ITALIANI[x],
        index=datetime.now().month - 1,
    )

# Recupera i dati del mese
monthly_expenses = get_expenses_by_month(pg_engine, selected_year, selected_month)
category_spending = get_category_spending(pg_engine, selected_year, selected_month)
targets = get_targets(pg_session)

# Statistiche generali
st.subheader(f"📅 Riepilogo {format_month_year(selected_year, selected_month)}")

if not monthly_expenses.empty:
    total_spent = monthly_expenses["amount"].sum()
    num_transactions = len(monthly_expenses)
    avg_transaction = total_spent / num_transactions if num_transactions > 0 else 0

    # Calcola target totale (solo target > 0) e verifica superamenti
    total_target = sum(v for v in targets.values() if v > 0) if targets else 0
    exceeded_categories = []
    has_any_targets = total_target > 0

    if targets:
        for category in CATEGORIES:
            spent = category_spending[category_spending["category"] == category][
                "total"
            ].sum()
            target = targets.get(category, 0)
            # Solo categorie con target impostato (> 0) e superato
            if target > 0 and spent > target:
                exceeded_categories.append(
                    {
                        "category": category,
                        "spent": spent,
                        "target": target,
                        "excess": spent - target,
                        "percentage": (spent / target * 100),
                    }
                )

    # Alert per superamento target (solo se ci sono target impostati)
    if has_any_targets and exceeded_categories:
        st.error(
            f"⚠️ **ATTENZIONE: {len(exceeded_categories)} {'categoria ha' if len(exceeded_categories) == 1 else 'categorie hanno'} superato il target mensile!**"
        )

        for cat in exceeded_categories:
            with st.expander(
                f"❌ **{cat['category']}**: Superamento di €{cat['excess']:.2f} ({cat['percentage']:.1f}% del target)",
                expanded=False,
            ):
                col1, col2, col3 = st.columns(3)
                col1.metric("Speso", f"€{cat['spent']:.2f}")
                col2.metric("Target", f"€{cat['target']:.2f}")
                col3.metric(
                    "Eccedenza",
                    f"€{cat['excess']:.2f}",
                    delta=f"+{cat['percentage'] - 100:.1f}%",
                    delta_color="inverse",
                )

    # Verifica budget totale (solo se ci sono target impostati)
    if has_any_targets:
        if total_spent > total_target:
            st.warning(
                f"⚠️ Il budget totale mensile di €{total_target:.2f} è stato superato di €{total_spent - total_target:.2f}"
            )
        else:
            remaining = total_target - total_spent
            st.success(
                f"✅ Sei in budget! Rimangono €{remaining:.2f} del budget mensile totale"
            )

    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Speso", f"€{total_spent:.2f}")
    col2.metric("Numero Transazioni", num_transactions)
    col3.metric("Media per Transazione", f"€{avg_transaction:.2f}")

    # Grafico a torta per categorie
    st.subheader("Distribuzione Spese per Categoria")
    fig_pie = px.pie(
        category_spending,
        values="total",
        names="category",
        title=f"Distribuzione Spese - {format_month_year(selected_year, selected_month)}",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Confronto con i target
    st.subheader("🎯 Confronto con i Target Mensili")

    if targets:
        comparison_data = []

        for category in CATEGORIES:
            spent = category_spending[category_spending["category"] == category][
                "total"
            ].sum()
            target = targets.get(category, 0)

            if target > 0 or spent > 0:
                percentage = (spent / target * 100) if target > 0 else 100
                status = (
                    "✅"
                    if spent <= target and target > 0
                    else "⚠️" if target > 0 else "➖"
                )

                comparison_data.append(
                    {
                        "Categoria": category,
                        "Speso": f"€{spent:.2f}",
                        "Target": f"€{target:.2f}" if target > 0 else "Non impostato",
                        "Percentuale": f"{percentage:.1f}%" if target > 0 else "N/A",
                        "Status": status,
                    }
                )

        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)

            # Grafico a barre confronto
            chart_data = []
            for category in CATEGORIES:
                spent = category_spending[category_spending["category"] == category][
                    "total"
                ].sum()
                target = targets.get(category, 0)

                if target > 0 or spent > 0:
                    chart_data.append(
                        {"Categoria": category, "Speso": spent, "Target": target}
                    )

            if chart_data:
                df_chart = pd.DataFrame(chart_data)
                fig_bar = go.Figure(
                    data=[
                        go.Bar(
                            name="Speso",
                            x=df_chart["Categoria"],
                            y=df_chart["Speso"],
                            marker_color="indianred",
                        ),
                        go.Bar(
                            name="Target",
                            x=df_chart["Categoria"],
                            y=df_chart["Target"],
                            marker_color="lightseagreen",
                        ),
                    ]
                )
                fig_bar.update_layout(
                    barmode="group",
                    title="Confronto Spese vs Target",
                    xaxis_title="Categoria",
                    yaxis_title="Importo (€)",
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Imposta dei target per vedere il confronto.")
    else:
        st.info(
            "Nessun target impostato. Vai alla sezione 'Imposta Target' per configurarli."
        )

    # Dettaglio transazioni del mese
    st.subheader("Dettaglio Transazioni")
    monthly_display = monthly_expenses.copy()
    monthly_display["date"] = monthly_display["date"].dt.strftime("%d/%m/%Y")
    monthly_display["amount"] = monthly_display["amount"].apply(lambda x: f"€{x:.2f}")

    st.dataframe(
        monthly_display[["date", "category", "amount", "description"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info(
        f"Nessuna spesa registrata per {format_month_year(selected_year, selected_month)}"
    )
