import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

from database.postgres_connection import init_postgres_db
from services.expense_service import CATEGORIES, get_monthly_totals, get_overall_monthly_totals

pg_engine, pg_session = init_postgres_db()
st.header("Andamento Temporale delle Spese")
st.set_page_config(page_title="Andamento Temporale delle Spese",
    page_icon="💰",
    layout="wide"
)
st.title("Andamento Temporale delle Spese")

# Selezione periodo
period = st.radio(
    "Seleziona il periodo da analizzare:",
    ["Ultimi 6 Mesi", "Ultimo Anno", "Ultimi 2 Anni", "Personalizzato"])

if period == "Ultimi 6 Mesi":
    end_date = date.today()
    start_date = end_date - relativedelta(months=6)
elif period == "Ultimo Anno":
    end_date = date.today()
    start_date = end_date - relativedelta(years=1)
elif period == "Ultimi 2 Anni":
    end_date = date.today()
    start_date = end_date - relativedelta(years=2)
else:  # Personalizzato
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data Inizio",
                                    value=date.today() -
                                    relativedelta(years=1))
    with col2:
        end_date = st.date_input("Data Fine", value=date.today())

# Recupera i dati
monthly_totals = get_monthly_totals(pg_session, start_date.strftime('%Y-%m-%d'),
                                        end_date.strftime('%Y-%m-%d'))

overall_totals = get_overall_monthly_totals(pg_session,
    start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

if not monthly_totals.empty:
    # Grafico andamento totale
    st.subheader("Andamento Spesa Totale Mensile")

    if not overall_totals.empty:
        fig_overall = px.line(overall_totals,
                                x='month',
                                y='total',
                                markers=True,
                                title="Spesa Totale Mensile")
        fig_overall.update_layout(xaxis_title="Mese",
                                    yaxis_title="Importo (€)")
        st.plotly_chart(fig_overall, use_container_width=True)

        # Statistiche generali
        avg_monthly = overall_totals['total'].mean()
        max_monthly = overall_totals['total'].max()
        min_monthly = overall_totals['total'].min()

        col1, col2, col3 = st.columns(3)
        col1.metric("Media Mensile", f"€{avg_monthly:.2f}")
        col2.metric("Massimo Mensile", f"€{max_monthly:.2f}")
        col3.metric("Minimo Mensile", f"€{min_monthly:.2f}")

    # Grafico per categoria
    st.subheader("Andamento per Categoria")

    fig_category = px.line(monthly_totals,
                            x='month',
                            y='total',
                            color='category',
                            markers=True,
                            title="Spesa Mensile per Categoria")
    fig_category.update_layout(xaxis_title="Mese",
                                yaxis_title="Importo (€)")
    st.plotly_chart(fig_category, use_container_width=True)

    # Media per categoria
    st.subheader("Media Spesa per Categoria")
    category_avg = monthly_totals.groupby(
        'category')['total'].mean().reset_index()
    category_avg.columns = ['Categoria', 'Media Mensile']
    category_avg = category_avg.sort_values('Media Mensile',
                                            ascending=False)
    category_avg['Media Mensile'] = category_avg['Media Mensile'].apply(
        lambda x: f"€{x:.2f}")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_avg = px.bar(monthly_totals.groupby('category')
                            ['total'].mean().reset_index().sort_values(
                                'total', ascending=False),
                            x='category',
                            y='total',
                            title="Media Mensile per Categoria")
        fig_avg.update_layout(xaxis_title="Categoria",
                                yaxis_title="Media (€)")
        st.plotly_chart(fig_avg, use_container_width=True)

    with col2:
        st.dataframe(category_avg,
                        use_container_width=True,
                        hide_index=True)

    # Sezione Previsioni
    st.divider()
    st.subheader("🔮 Previsioni Spese Future")

    st.info(
        "💡 Le previsioni sono basate sulla media mobile degli ultimi mesi e mostrano una stima delle spese future."
    )

    # Calcola previsioni solo se abbiamo almeno 3 mesi di dati
    if len(overall_totals) >= 3:
        # Numero di mesi da prevedere
        forecast_months = st.slider("Mesi da prevedere:",
                                    min_value=1,
                                    max_value=6,
                                    value=3)

        # Calcola il trend usando regressione lineare
        if len(overall_totals) >= 6:
            # Usa gli ultimi 6 mesi per calcolare il trend
            recent_values = overall_totals.tail(6)['total'].values
            x = list(range(len(recent_values)))

            # Calcola coefficienti regressione lineare (slope e intercept)
            n = len(x)
            x_mean = sum(x) / n
            y_mean = sum(recent_values) / n
            numerator = sum((x[i] - x_mean) * (recent_values[i] - y_mean)
                            for i in range(n))
            denominator = sum((x[i] - x_mean)**2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean

            # L'ultimo valore della serie è il punto di partenza per le previsioni
            last_value = recent_values[-1]
            base_index = len(recent_values) - 1
        else:
            # Se non ci sono abbastanza dati, usa la media semplice
            slope = 0
            intercept = 0
            last_value = overall_totals.tail(3)['total'].mean()
            base_index = 0

        # Genera previsioni
        last_month = overall_totals.iloc[-1]['month']
        last_date = pd.to_datetime(last_month + '-01')

        forecast_data = []

        for i in range(1, forecast_months + 1):
            future_date = last_date + relativedelta(months=i)
            future_month = future_date.strftime('%Y-%m')

            # Calcola previsione usando la regressione lineare
            if len(overall_totals) >= 6:
                # Proietta il trend dal valore attuale
                prediction_value = last_value + (slope * i)
            else:
                # Usa la media se non c'è abbastanza storico per il trend
                prediction_value = last_value

            # Assicurati che la previsione non sia negativa
            prediction_value = max(prediction_value, 0)

            forecast_data.append({
                'month': future_month,
                'total': prediction_value,
                'type': 'Previsione'
            })

        # Combina dati storici e previsioni
        historical_data = overall_totals.copy()
        historical_data['type'] = 'Storico'

        df_forecast = pd.DataFrame(forecast_data)
        combined_data = pd.concat([historical_data, df_forecast],
                                    ignore_index=True)

        # Grafico con dati storici e previsioni
        fig_forecast = go.Figure()

        # Linea storica
        historical = combined_data[combined_data['type'] == 'Storico']
        fig_forecast.add_trace(
            go.Scatter(x=historical['month'],
                        y=historical['total'],
                        mode='lines+markers',
                        name='Spese Storiche',
                        line=dict(color='royalblue', width=2),
                        marker=dict(size=8)))

        # Linea previsione
        forecast = combined_data[combined_data['type'] == 'Previsione']
        # Aggiungi l'ultimo punto storico per continuità
        last_historical = historical.iloc[-1]
        forecast_with_last = pd.concat([
            pd.DataFrame([{
                'month': last_historical['month'],
                'total': last_historical['total']
            }]), forecast
        ],
                                        ignore_index=True)

        fig_forecast.add_trace(
            go.Scatter(x=forecast_with_last['month'],
                        y=forecast_with_last['total'],
                        mode='lines+markers',
                        name='Previsioni',
                        line=dict(color='coral', width=2, dash='dash'),
                        marker=dict(size=8, symbol='diamond')))

        # Area di confidenza (±15% della previsione)
        upper_bound = forecast_with_last['total'] * 1.15
        lower_bound = forecast_with_last['total'] * 0.85

        fig_forecast.add_trace(
            go.Scatter(x=forecast_with_last['month'],
                        y=upper_bound,
                        mode='lines',
                        name='Limite Superiore',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'))

        fig_forecast.add_trace(
            go.Scatter(x=forecast_with_last['month'],
                        y=lower_bound,
                        mode='lines',
                        name='Intervallo di Confidenza',
                        fill='tonexty',
                        fillcolor='rgba(255, 127, 80, 0.2)',
                        line=dict(width=0),
                        showlegend=True))

        fig_forecast.update_layout(
            title="Andamento Storico e Previsioni Spese Mensili",
            xaxis_title="Mese",
            yaxis_title="Importo (€)",
            hovermode='x unified')

        st.plotly_chart(fig_forecast, use_container_width=True)

        # Mostra statistiche previsioni
        col1, col2, col3 = st.columns(3)
        # Calcola la media delle previsioni effettive
        avg_forecast = sum(f['total'] for f in forecast_data) / len(
            forecast_data) if forecast_data else 0
        col1.metric("Media Prevista Mensile", f"€{avg_forecast:.2f}")
        total_forecast = sum(f['total'] for f in forecast_data)
        col2.metric(f"Totale Previsto ({forecast_months} mesi)",
                    f"€{total_forecast:.2f}")

        trend_text = "In crescita" if slope > 0 else "In diminuzione" if slope < 0 else "Stabile"
        trend_icon = "📈" if slope > 0 else "📉" if slope < 0 else "➡️"
        col3.metric("Tendenza", f"{trend_icon} {trend_text}")

        # Previsioni per categoria
        st.subheader("Previsioni per Categoria")

        category_forecasts = []
        for category in CATEGORIES:
            category_data = monthly_totals[monthly_totals['category'] ==
                                            category]
            if not category_data.empty and len(category_data) >= 3:
                cat_avg = category_data.tail(3)['total'].mean()
                cat_forecast = cat_avg * forecast_months

                category_forecasts.append({
                    'Categoria':
                    category,
                    'Media Mensile':
                    f"€{cat_avg:.2f}",
                    f'Totale {forecast_months} Mesi':
                    f"€{cat_forecast:.2f}"
                })

        if category_forecasts:
            df_cat_forecast = pd.DataFrame(category_forecasts).sort_values(
                f'Totale {forecast_months} Mesi',
                key=lambda x: x.str.replace('€', '').astype(float),
                ascending=False)
            st.dataframe(df_cat_forecast,
                            use_container_width=True,
                            hide_index=True)

            # Grafico previsioni per categoria
            fig_cat_forecast = px.bar(
                df_cat_forecast,
                x='Categoria',
                y=f'Totale {forecast_months} Mesi',
                title=
                f"Previsioni Totali per Categoria ({forecast_months} Mesi)",
                color=f'Totale {forecast_months} Mesi',
                color_continuous_scale='Oranges')
            # Converti i valori stringa in numeri per il grafico
            cat_forecast_values = [
                float(x['Totale ' + str(forecast_months) +
                        ' Mesi'].replace('€', ''))
                for x in category_forecasts
            ]
            fig_cat_forecast.data[0].y = cat_forecast_values
            fig_cat_forecast.update_layout(
                xaxis_title="Categoria",
                yaxis_title="Importo Totale Previsto (€)",
                showlegend=False)
            st.plotly_chart(fig_cat_forecast, use_container_width=True)
        else:
            st.info(
                "Dati insufficienti per le previsioni per categoria (servono almeno 3 mesi di dati)."
            )
    else:
        st.warning(
            "⚠️ Servono almeno 3 mesi di dati storici per generare previsioni attendibili."
        )

else:
    st.info("Nessun dato disponibile per il periodo selezionato.")
