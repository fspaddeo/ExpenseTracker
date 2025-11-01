# Usa un'immagine Python ufficiale
FROM python:3.13-slim

# Imposta la working directory
WORKDIR /app

# Copia requirements.txt e installa le dipendenze
COPY requirements.txt .
# COPY /etc/secrets/secrets.toml ./.streamlit/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice dentro /app
COPY src/ ./src

# Esponi la porta di Streamlit
EXPOSE 8501

# Imposta variabile d'ambiente per Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando per avviare Streamlit
CMD ["streamlit", "run", "src/create_expense.py"]
