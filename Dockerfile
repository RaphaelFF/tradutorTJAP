# Utilizar uma imagem base do Python
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de dependências (requirements.txt)
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação para dentro do container
COPY . .

# Expor a porta que a FastAPI irá rodar (normalmente a porta 8000)
EXPOSE 8000
# Comando para rodar a aplicação
CMD uvicorn app:app --reload 
