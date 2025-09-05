import os
import re
import pdfplumber
import io
from flask import Flask, request, render_template, redirect, url_for

from data.export import exportar_excel
from data.readcontrol import buscar_referencia_no_excel, ARQUIVO_CONTROLE
from data.readdb import buscar_descricao_no_excel, ARQUIVO_BANCO
from data.formatacao import formato_brasileiro


app = Flask(__name__)

# Armazena resultados em memória para que não se percam a cada requisição
resultados = {}
nf_filhas = {}  # dicionário global para armazenar os inputs "NF Filha"

PIS = 1.75
COFINS = 7.60


# Registra o filtro no Jinja2 do Flask
app.jinja_env.filters['br'] = formato_brasileiro
app.jinja_env.filters['moeda'] = formato_brasileiro
app.jinja_env.filters['real'] = formato_brasileiro


def extrair_dados(pdf_path):

    dados = {}
    despesas = []
    soma_valores_liquidos = 0.00

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

        # --- Regex modificado para capturar múltiplas referências ---
        ref_match = re.search(r"Referência:\s*([^;\n]+(?:;\s*[^;\n]+)*)", text)
        if ref_match:
            referencias_texto = ref_match.group(1).strip()
            # Separa as referências por ponto e vírgula
            referencias_lista = [ref.strip()
                                 for ref in referencias_texto.split(';')]
            dados["Referências"] = referencias_lista
            # Mantém compatibilidade
            dados["Referência"] = referencias_lista[0]
        else:
            dados["Referências"] = ["Não Encontrado"]
            dados["Referência"] = "Não Encontrado"

        imp_match = re.search(r"Importador/Exportador:\s*([^;\n]+)", text)
        dados["Importador/Exportador"] = imp_match.group(
            1).strip() if imp_match else "Não Encontrado"

        total_match = re.search(r"Total não Trib.*: ([\d.,]+)", text)
        dados["Total não Trib."] = total_match.group(1) if total_match else "0"

        # --- Busca no Excel para cada referência ---
        dados_referencias = []

        for referencia in dados["Referências"]:
            if referencia != "Não Encontrado":
                resultado = buscar_referencia_no_excel(
                    referencia, ARQUIVO_CONTROLE)
                if resultado:
                    (valor_icms_excel, valor_nfmae_excel, valor_cfop_excel,
                     valor_n_doc_excel, valor_contabil_excel, valor_parceiro_excel) = resultado

                    icms_formatado = f"{valor_icms_excel * 100:.2f}%" if valor_icms_excel is not None and isinstance(
                        valor_icms_excel, (int, float)) else "Não Encontrado"

                    dados_ref = {
                        "Referência": referencia,
                        "ICMS%": icms_formatado,
                        "NFMAE": valor_nfmae_excel if valor_nfmae_excel is not None else "Não Encontrado",
                        "CFOP": valor_cfop_excel if valor_cfop_excel is not None else "Não Encontrado",
                        "Nº DOC": valor_n_doc_excel if valor_n_doc_excel is not None else "Não Encontrado",
                        "CONTABIL": valor_contabil_excel if valor_contabil_excel is not None else "Não Encontrado",
                        "PARCEIRO": valor_parceiro_excel if valor_parceiro_excel is not None else "Não Encontrado"
                    }
                    dados_referencias.append(dados_ref)
                else:
                    # Se não encontrou dados para esta referência
                    dados_ref = {
                        "Referência": referencia,
                        "ICMS%": "Não Encontrado",
                        "NFMAE": "Não Encontrado",
                        "CFOP": "Não Encontrado",
                        "Nº DOC": "Não Encontrado",
                        "CONTABIL": "Não Encontrado",
                        "PARCEIRO": "Não Encontrado"
                    }
                    dados_referencias.append(dados_ref)

        dados["DadosReferencias"] = dados_referencias

        # Mantém os campos originais para compatibilidade (usando a primeira referência)
        if dados_referencias:
            primeira_ref = dados_referencias[0]
            dados["ICMS%"] = primeira_ref["ICMS%"]
            dados["NFMAE"] = primeira_ref["NFMAE"]
            dados["CFOP"] = primeira_ref["CFOP"]
            dados["Nº DOC"] = primeira_ref["Nº DOC"]
            dados["CONTABIL"] = primeira_ref["CONTABIL"]
            dados["PARCEIRO"] = primeira_ref["PARCEIRO"]
        else:
            dados["ICMS%"] = "Não Encontrado"
            dados["NFMAE"] = "Não Encontrado"
            dados["CFOP"] = "Não Encontrado"
            dados["Nº DOC"] = "Não Encontrado"
            dados["CONTABIL"] = "Não Encontrado"
            dados["PARCEIRO"] = "Não Encontrado"

        # --- Extrai tabela de despesas ---
        bloco_despesas = re.search(
            r"Discriminação das despesas.*?([\s\S]*?)Total não Trib", text)
        if bloco_despesas:
            linhas = bloco_despesas.group(1).strip().split("\n")
            for linha in linhas:
                if "não tributável Pagas pela Comissária" in linha:
                    continue
                partes = linha.rsplit(" ", 1)
                if len(partes) == 2:
                    descricao = partes[0].strip()
                    valor_str = partes[1].strip()

                    valor_limpo = valor_str.replace("R$", "").strip()
                    if "," in valor_limpo:
                        valor_para_calculo = valor_limpo.replace(
                            ".", "").replace(",", ".")
                    else:
                        valor_para_calculo = valor_limpo

                    try:
                        valor_float = float(valor_para_calculo)

                        classificacao_excel = buscar_descricao_no_excel(
                            descricao, ARQUIVO_BANCO)
                        # soma aqui 👇
                        soma_valores_liquidos += valor_float

                        despesas.append({
                            "Descrição": descricao,
                            "valorInt": valor_float,
                            "Valor": valor_limpo,
                            "ValorBruto": valor_str,
                            "Classificação": classificacao_excel if classificacao_excel else "Não Encontrado",
                            "Total Liquido": soma_valores_liquidos
                        })

                    except ValueError:
                        continue

    except Exception as e:
        print(f"Erro ao extrair dados do PDF {pdf_path}: {e}")
        return {}, []

    return dados, despesas


@app.route("/exportar")
def exportar():
    return exportar_excel(resultados, nf_cache)


# --- Rotas da Aplicação Flask ---
@app.route('/')
def index():
    return render_template('index.html', arquivos=list(resultados.keys()), nf_filhas=nf_filhas)


nf_cache = {}  # dicionário em memória (doc -> {row -> value})


@app.route("/salvar_nf_filha", methods=["POST"])
def salvar_nf_filha():
    data = request.get_json()
    doc = data["doc"]
    row = data["row"]
    value = data["value"]

    if doc not in nf_cache:
        nf_cache[doc] = {}
    nf_cache[doc][row] = value

    return {"status": "ok"}


@app.route("/remover_doc", methods=["POST"])
def remover_doc():
    data = request.get_json()
    nome = data["nome"]
    if nome in resultados:
        del resultados[nome]
    return {"status": "ok"}


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


@app.route("/doc/<nome>")
def mostrar_doc(nome):
    if nome not in resultados:
        return "Documento não encontrado", 404

    dados = resultados[nome]["dados"]
    despesas = resultados[nome]["despesas"]

    # valores já salvos para este doc
    nf_filhas_doc = nf_cache.get(nome, {})

    return render_template(
        "index.html",
        arquivos=list(resultados.keys()),
        dados=dados,
        despesas=despesas,
        ativo=nome,
        nf_filhas=nf_filhas_doc
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
