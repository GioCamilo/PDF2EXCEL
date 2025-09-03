import openpyxl

# Caminho para o banco de dados
ARQUIVO_BANCO = 'documentos/bancoDados.xlsm'

def buscar_descricao_no_excel(descricao, excel_path=ARQUIVO_BANCO):
    """
    Busca uma descrição na coluna A do arquivo Excel e retorna
    o valor da coluna B correspondente.

    Args:
        descricao (str): O valor da descrição a ser buscado.
        excel_path (str): O caminho para o arquivo Excel.

    Returns:
        any: O valor da coluna B encontrado, ou None se não for encontrado.
    """
    try:
        # Carrega a planilha
        workbook = openpyxl.load_workbook(excel_path, data_only=True)
        sheet = workbook.active

        # Itera pelas linhas procurando a descrição na coluna A
        for row in sheet.iter_rows(min_row=1):
            celula_descricao = row[0]  # Coluna A (índice 0)
            if celula_descricao.value and str(celula_descricao.value).strip() == descricao.strip():
                valor_coluna_b = row[1].value  # Coluna B (índice 1)
                print(f"Descrição '{descricao}' encontrada. Valor da coluna B: {valor_coluna_b}")
                return valor_coluna_b

    except FileNotFoundError:
        print(f"Erro: O arquivo '{excel_path}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo Excel: {e}")
        return None

    print(f"Aviso: Descrição '{descricao}' não encontrada na planilha.")
    return None
