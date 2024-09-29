import fitz  # PyMuPDF
import google.generativeai as genai
import psycopg2
import re
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Configurando a API do Google Generative AI
GOOGLE_API_KEY = "AIzaSyBBIfJTI973pSnol3UBsH3TPxmg1kqhmug"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    'gemini-1.0-pro',
    generation_config=genai.GenerationConfig(
        max_output_tokens=2000,
        temperature=0.9,
    )
)

# Configuração do banco de dados
def conectar_db():
    conn = psycopg2.connect(
        dbname="glossario_legal",
        user="postgres",
        password="4026",
        host="localhost"
    )
    return conn

# Consulta de termos no banco de dados
def verificar_termos(texto):
    conn = conectar_db()
    cur = conn.cursor()
    termos_encontrados = {}
    cur.execute("SELECT termo, definicao FROM termos_juridicos")
    rows = cur.fetchall()

    for row in rows:
        termo, definicao = row
        if re.search(r'\b' + re.escape(termo) + r'\b', texto, re.IGNORECASE):
            termos_encontrados[termo] = definicao
    cur.close()
    conn.close()
    return termos_encontrados

# Função para simplificar termos
def simplificar_termos(termo, definicao, texto):
    mensagem = (f"Atue como um especialista de simplificação de termos jurídicos para a comunidade "
                f"e responda com base no texto: {texto}, e na definição do termo jurídico, termo: {termo}, "
                f"sua definição é: {definicao}. 1. Duas palavras que podem substituir essa palavra. "
                f"2. Como o {termo} está sendo usado no contexto do texto.")

    resposta = model.generate_content(
        mensagem,
        generation_config=genai.GenerationConfig(
            max_output_tokens=100,
            temperature=0.7,
        )
    )
    return resposta.text

# Processamento de PDF
def processar_pdf(input_pdf_path, output_pdf_path):
    pdf_document = fitz.open(input_pdf_path)
    page_count = pdf_document.page_count

    for page_number in range(page_count):
        page = pdf_document.load_page(page_number)
        texto = page.get_text()
        termos_encontrados = verificar_termos(texto)

        if termos_encontrados:
            for termo, definicao in termos_encontrados.items():
                sugestoes = simplificar_termos(termo, definicao, texto)

                text_instances = page.search_for(termo)
                for inst in text_instances:
                    link_rect = fitz.Rect(inst)
                    page.add_freetext_annot(link_rect, sugestoes, fontsize=1, rotate=0)

    pdf_document.save(output_pdf_path)
    pdf_document.close()

# Endpoint para upload e processamento de PDF
@app.post("/process_pdf/")
async def process_pdf(file: UploadFile = File(...)):
    input_path = "input.pdf"
    output_path = "output.pdf"

    # Salvando o arquivo PDF enviado
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Processando o PDF
    processar_pdf(input_path, output_path)

    # Retornando o arquivo PDF processado
    return FileResponse(output_path, media_type='application/pdf', filename='output.pdf')

