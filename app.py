import os
import re
import pdfplumber
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Armazena resultados em memória
resultados = {}

def extrair_dados(pdf_path):
    dados = {}
    despesas = []

    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

        # --- Regex para campos fixos ---
       
        dados["Referência"] = re.search(r"Referência:\s*(.+)", text).group(1) 
        dados["Total não Trib."] = re.search(r"Total não Trib.*: ([\d.,]+)", text).group(1)
       
        # --- Tabela de despesas ---
        bloco_despesas = re.search(r"Discriminação das despesas.*?([\s\S]*?)Total não Trib", text)
        if bloco_despesas:
            linhas = bloco_despesas.group(1).strip().split("\n")
            for linha in linhas:
                if "não tributável Pagas pela Comissária" in linha:
                    continue
                partes = linha.rsplit(" ", 1)
                if len(partes) == 2:
                    despesas.append({"Descrição": partes[0].strip(), "Valor": partes[1].strip()})

    return dados, despesas


@app.route('/')
def index():
    # Renderiza sem dados (apenas com os arquivos já enviados)
    return render_template('index.html', arquivos=list(resultados.keys()))


@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist("files")
    if not files:
        return "Nenhum arquivo enviado", 400

    os.makedirs("temp", exist_ok=True)

    for file in files:
        if file and file.filename:
            file_path = os.path.join("temp", file.filename)
            file.save(file_path)
            dados, despesas = extrair_dados(file_path)
            resultados[file.filename] = {"dados": dados, "despesas": despesas}

    return redirect(url_for("index"))


@app.route('/doc/<nome>')
def mostrar_doc(nome):
    if nome not in resultados:
        return "Documento não encontrado", 404
    return render_template('index.html',
                           arquivos=list(resultados.keys()),
                           dados=resultados[nome]["dados"],
                           despesas=resultados[nome]["despesas"],
                           ativo=nome)


if __name__ == '__main__':
    app.run(debug=True)
