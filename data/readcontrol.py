
import openpyxl

# Caminho para o arquivo de controle
ARQUIVO_CONTROLE = 'documentos/controle.xlsx'

# Cache em memória para as referências
_excel_cache = {}


def carregar_excel_controle():
    """
    Carrega os dados do Excel de controle em memória (cache).
    Cada referência vira uma chave em _excel_cache.
    """
    global _excel_cache
    _excel_cache = {}

    try:
        workbook = openpyxl.load_workbook(ARQUIVO_CONTROLE, data_only=True)
        sheet = workbook.active

        # Itera sobre todas as linhas da planilha
        for row in sheet.iter_rows(min_row=2, values_only=False):
            ref_cell = row[29]  # coluna 30 no Excel (índice 29)
            if ref_cell.value:
                referencia = str(ref_cell.value).strip()
                _excel_cache[referencia] = (
                    row[26].value,  # ICMS%
                    row[6].value,   # NFMAE
                    row[12].value,  # CFOP
                    row[5].value,   # Nº DOC
                    row[23].value,  # Conta Contábil
                    row[10].value   # Parceiro
                )

        print(f"[CACHE] {len(_excel_cache)} referências carregadas do Excel.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{ARQUIVO_CONTROLE}' não foi encontrado.")
        _excel_cache = {}
    except Exception as e:
        print(f"Erro ao carregar Excel: {e}")
        _excel_cache = {}


def buscar_referencia_no_excel(referencia, excel_path=None):
    """
    Busca uma referência no cache em memória.
    Se não for encontrada, retorna tupla de None.
    """
    if not _excel_cache:
        carregar_excel_controle()

    return _excel_cache.get(referencia.strip(), (None, None, None, None, None, None))
