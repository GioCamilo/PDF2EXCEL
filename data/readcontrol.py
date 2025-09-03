
import openpyxl



# Caminho para o arquivo de controle. Certifique-se de que o arquivo está nesse caminho.
ARQUIVO_CONTROLE = 'documentos/controle.xlsx'

def buscar_referencia_no_excel(referencia, excel_path):
    """
    Busca uma referência (chave) na coluna 29 de um arquivo Excel e retorna
    o valor da coluna 28 (ICMS%).
    
    Args:
        referencia (str): O valor da referência a ser buscado (vindo do PDF).
        excel_path (str): O caminho para o arquivo Excel de controle.

    Returns:
        any: O valor da célula encontrada na coluna 28, ou None se não for encontrado.
    """
    try:
        # Carrega a pasta de trabalho do Excel
        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook.active
        
        # Itera sobre todas as linhas da planilha de forma eficiente
        for row in sheet.iter_rows():
            # Acessa a célula da coluna 29 (índice 28), que é a nossa chave de busca
            celula_referencia = row[29]
            
            # Compara o valor da célula com a referência extraída do PDF
            if celula_referencia.value and str(celula_referencia.value).strip() == referencia.strip():
                # Se a referência foi encontrada, pegamos o valor da coluna 28 (índice 27)
                valor_icms = row[26].value
                valor_nfmae = row[6].value
                valor_cfop = row[12].value
                valor_n_doc = row[5].value
                valor_contabil = row[23].value
                valor_parceiro = row[10].value
             
                

            
             
                
                # Imprime uma mensagem de confirmação no console para depuração
                print(f"Valor de ICMS% encontrado: '{valor_icms}' para a Referência: '{referencia}'")
                print(f"Valor de NFMAE encontrado: '{valor_nfmae}' para a Referência: '{referencia}'") 
                print(f"Valor de CFOP encontrado: '{valor_cfop}' para a Referência: '{referencia}'")    
                print(f"Valor de Processo encontrado: '{valor_n_doc}' para a Referência: '{referencia}'")     
                print(f"Valor de Conta Contábil encontrado: '{valor_contabil}' para a Referência: '{referencia}'") 
                print(f"Valor de Parceiro encontrado: '{valor_parceiro}' para a Referência: '{referencia}'")     
                # Retorna o valor de ICMS% encontrado
                return valor_icms, valor_nfmae, valor_cfop, valor_n_doc, valor_contabil, valor_parceiro
        
    except FileNotFoundError:
        # Se o arquivo não for encontrado, imprime um erro no console
        print(f"Erro: O arquivo de controle '{excel_path}' não foi encontrado.")
        return None
    except Exception as e:
        # Captura qualquer outro erro que possa ocorrer ao ler o arquivo
        print(f"Ocorreu um erro ao ler o arquivo Excel: {e}")
        return None
    
    # Se o loop terminar e a referência não for encontrada, retorna None
    print(f"Aviso: Referência '{referencia}' não encontrada na planilha.")
    return None