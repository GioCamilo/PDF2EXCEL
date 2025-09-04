import re
import pdfplumber
from data.readcontrol import buscar_referencia_no_excel, ARQUIVO_CONTROLE
from data.readdb import buscar_descricao_no_excel, ARQUIVO_BANCO


PIS = None
CONFINS = None

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
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

        # --- Regex com validação ---
        ref_match = re.search(r"Referência:\s*(MRE\d+)", text)
        dados["Referência"] = ref_match.group(1).strip() if ref_match else "Não Encontrado"

        imp_match = re.search(r"Importador/Exportador:\s*([^;\n]+)", text)
        dados["Importador/Exportador"] = imp_match.group(1).strip() if imp_match else "Não Encontrado"

        total_match = re.search(r"Total não Trib.*: ([\d.,]+)", text)
        dados["Total não Trib."] = total_match.group(1) if total_match else "0"

        # --- Busca no Excel ---
        resultado = buscar_referencia_no_excel(dados["Referência"], ARQUIVO_CONTROLE)
        if resultado:
            (valor_icms_excel, valor_nfmae_excel, valor_cfop_excel,
             valor_n_doc_excel, valor_contabil_excel, valor_parceiro_excel) = resultado
        else:
            valor_icms_excel = valor_nfmae_excel = valor_cfop_excel = None
            valor_n_doc_excel = valor_contabil_excel = valor_parceiro_excel = None

        if valor_icms_excel is not None and isinstance(valor_icms_excel, (int, float)):
            dados["ICMS%"] = f"{valor_icms_excel * 100:.2f}%"
        else:
            dados["ICMS%"] = "Não Encontrado"

        dados["NFMAE"] = valor_nfmae_excel if valor_nfmae_excel is not None else "Não Encontrado"
        dados["CFOP"] = valor_cfop_excel if valor_cfop_excel is not None else "Não Encontrado"
        dados["Nº DOC"] = valor_n_doc_excel if valor_n_doc_excel is not None else "Não Encontrado"
        dados["CONTABIL"] = valor_contabil_excel if valor_contabil_excel is not None else "Não Encontrado"
        dados["PARCEIRO"] = valor_parceiro_excel if valor_parceiro_excel is not None else "Não Encontrado"

        # --- Extrai tabela de despesas ---
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

                    # Limpeza e conversão do valor
                    valor_limpo = valor_str.replace("R$", "").strip()
                    
                    # Para cálculos internos, converte para float
                    if "," in valor_limpo:
                        valor_para_calculo = valor_limpo.replace(".", "").replace(",", ".")
                    else:
                        valor_para_calculo = valor_limpo

                    try:
                        valor_float = float(valor_para_calculo)  # Para cálculos internos
                        valor_int = int(valor_float)

                        classificacao_excel = buscar_descricao_no_excel(descricao, ARQUIVO_BANCO)


                        despesas.append({
                            "Descrição": descricao,
                            "valorInt": valor_float,
                            "Valor": valor_limpo,  # Mantém formato brasileiro: 19.894,43
                            "ValorBruto": valor_str,
                            "ValorPIS": PIS,
                            "ValorCOFINS": CONFINS,
                            "Classificação": classificacao_excel if classificacao_excel is not None else "Não Encontrado"
                        })


                        
                        
                    except ValueError:
                        # Tratamento de erro caso não seja possível converter o valor
                        continue

    except Exception as e:
        print(f"Erro ao extrair dados do PDF {pdf_path}: {e}")
        return {}, []

    return dados, despesas
