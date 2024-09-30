# Utilizar uma imagem base do Python
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

COPY ./app

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta que a FastAPI irá rodar (normalmente a porta 8000)
EXPOSE 8000

# Comando para rodar a aplicação
CMD python -m uvicorn app:app  --host 0.0.0.0 --port 8000 --reload
