import openpyxl

# Caminho para o banco de dados
ARQUIVO_BANCO = 'documentos/bancoDados.xlsm'

_descricao_cache = {}


def carregar_excel_banco():
    """
    Carrega os dados do Excel de banco em memória (cache).
    Cada descrição vira uma chave em _descricao_cache.
    """
    global _descricao_cache
    _descricao_cache = {}

    try:
        workbook = openpyxl.load_workbook(ARQUIVO_BANCO, data_only=True)
        sheet = workbook.active

        # Itera sobre todas as linhas da planilha
        for row in sheet.iter_rows(min_row=1, values_only=False):
            desc_cell = row[0]  # coluna A no Excel (índice 0)
            if desc_cell.value:
                descricao = str(desc_cell.value).strip()
                _descricao_cache[descricao] = row[1].value  # Coluna B

        print(
            f"[CACHE] {len(_descricao_cache)} descrições carregadas do Excel.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{ARQUIVO_BANCO}' não foi encontrado.")
        _descricao_cache = {}
    except Exception as e:
        print(f"Erro ao carregar Excel: {e}")
        _descricao_cache = {}


def buscar_descricao_no_excel(descricao, excel_path=ARQUIVO_BANCO):
    """
    Busca uma descrição no cache em memória.
    Se não for encontrada, retorna None.
    """
    if not _descricao_cache:
        carregar_excel_banco()

    return _descricao_cache.get(descricao.strip(), None)
