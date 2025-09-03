import os
import re
import pdfplumber
from flask import Flask, request, render_template, redirect, url_for
from data.readcontrol import buscar_referencia_no_excel, ARQUIVO_CONTROLE
from data.readdb import buscar_descricao_no_excel, ARQUIVO_BANCO


app = Flask(__name__)


# Armazena resultados em memória para que não se percam a cada requisição
resultados = {}
PIS = bool(1.75)
COFINS = bool(7.60)

def extrair_dados(pdf_path):
    """
    Extrai dados de um arquivo PDF e busca informações adicionais em um arquivo Excel.
    
    Args:
        pdf_path (str): O caminho para o arquivo PDF.

    Returns:
        tuple: Um par de dicionários contendo os dados do cabeçalho e as despesas.
    """
    dados = {}
    despesas = []

    try:
        # Abre o arquivo PDF para extração de texto
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"


            # Usa Regex para extrair campos fixos do PDF
            dados["Referência"] = re.search(r"Referência:\s*([^;]+);", text).group(1).strip()
            dados["Importador/Exportador"] = re.search(r"Importador/Exportador:\s*([^;]+);", text).group(1).strip()
            dados["Total não Trib."] = re.search(r"Total não Trib.*: ([\d.,]+)", text).group(1)

            # Busca o valor de ICMS% na planilha usando a Referência como chave
            valor_icms_excel, valor_nfmae_excel, valor_cfop_excel, valor_n_doc_excel, valor_contabil_excel, valor_parceiro_excel  = buscar_referencia_no_excel(dados["Referência"], ARQUIVO_CONTROLE)
            
            # Adiciona o valor encontrado (ou 'Não Encontrado') aos dados
            dados["ICMS%"] = valor_icms_excel if valor_icms_excel is not None else "Não Encontrado"
            dados["NFMAE"] = valor_nfmae_excel if valor_nfmae_excel is not None else "Não Encontrado"
            dados["CFOP"] = valor_cfop_excel if valor_cfop_excel is not None else "Não Encontrado"
            dados["Nº DOC"] = valor_n_doc_excel if valor_n_doc_excel is not None else "Não Encontrado"
            dados["CONTABIL"] = valor_contabil_excel if valor_contabil_excel is not None else "Não encontrado"
            dados["PARCEIRO"] = valor_parceiro_excel if valor_parceiro_excel is not None else "Não encontrado"
           

            # Extrai a tabela de despesas usando Regex
            bloco_despesas = re.search(r"Discriminação das despesas.*?([\s\S]*?)Total não Trib", text)
            if bloco_despesas:
                linhas = bloco_despesas.group(1).strip().split("\n")
                for linha in linhas:
                    if "não tributável Pagas pela Comissária" in linha:
                        continue
                    partes = linha.rsplit(" ", 1)
                    if len(partes) == 2:
                        descricao = partes[0].strip()
                        valor_str = partes[1].strip()

                        # LIMPANDO E CONVERTENDO O VALOR
                        # 1. Remove o R$ e o ponto de milhar
                        valor_limpo = valor_str.replace("R$", "").replace(".", "")
                        # 2. Troca a vírgula pelo ponto
                        valor_final_str = valor_limpo.replace(",", ".")

                        
                        
                        try:
                            # 3. Converte para float para manter os centavos
                            valor_float = float(valor_final_str)
                            # 4. (OPCIONAL) Converte para int, se necessário
                            valor_int = int(valor_float)

                            classificacao_excel = buscar_descricao_no_excel(descricao, ARQUIVO_BANCO)
                            # Adiciona o dicionário com os valores convertidos
                            despesas.append({
                            "Descrição": descricao,
                            "valorInt": valor_float,
                            "Valor": valor_int,
                            "ValorBruto": valor_str,
                            "ValorPIS": PIS,
                            "ValorCOFINS": COFINS,
                            "Classificação": classificacao_excel if classificacao_excel is not None else "Não Encontrado"
                            })

                        except ValueError:
                            print(f"Não foi possível converter o valor: '{valor_str}'")

        
            

 
          
                        
            
    except Exception as e:
        print(f"Erro ao extrair dados do PDF {pdf_path}: {e}")
        return {}, []

    return dados, despesas

# --- Rotas da Aplicação Flask ---
# Rota principal para a página inicial
@app.route('/')
def index():
    return render_template('index.html', arquivos=list(resultados.keys()))

# Rota para o upload de arquivos PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist("files")
    if not files:
        return "Nenhum arquivo enviado", 400

    # Cria a pasta temporária se ela não existir
    os.makedirs("temp", exist_ok=True)

    # Processa cada arquivo enviado
    for file in files:
        if file and file.filename:
            file_path = os.path.join("temp", file.filename)
            file.save(file_path)
            # Extrai os dados do PDF e do Excel
            dados, despesas = extrair_dados(file_path)
            # Armazena os dados extraídos em memória
            resultados[file.filename] = {"dados": dados, "despesas": despesas}

    return redirect(url_for("index"))

# Rota para exibir os dados de um documento específico
@app.route('/doc/<nome>')
def mostrar_doc(nome):
    if nome not in resultados:
        return "Documento não encontrado", 404
    # Renderiza o template com os dados do documento selecionado
    return render_template('index.html',
                           arquivos=list(resultados.keys()),
                           dados=resultados[nome]["dados"],
                           despesas=resultados[nome]["despesas"],
                           ativo=nome)

if __name__ == '__main__':
    app.run(debug=True)