FROM python:3.10-slim

# Instalar dependências do sistema (inclui Poppler e Tesseract)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    && apt-get clean

# Criar diretório do app
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

