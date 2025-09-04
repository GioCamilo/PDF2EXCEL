

# ===============================================
# FILTRO BRASILEIRO PARA JINJA2
# ===============================================
def formato_brasileiro(valor):

    if valor is None:
        return "0,00"
    
    try:
        # Converte para float se necessário
        if isinstance(valor, str):
            if "," in valor:
                # Se já está no formato brasileiro, converte para float
                valor_temp = valor.replace(".", "").replace(",", ".")
                valor = float(valor_temp)
            else:
                valor = float(valor)
        
        # Se o valor é 0
        if valor == 0:
            return "0,00"
        
        # Formata com 2 casas decimais
        valor_formatado = f"{float(valor):.2f}"
        
        # Separa parte inteira e decimal
        partes = valor_formatado.split('.')
        parte_inteira = partes[0]
        parte_decimal = partes[1]
        
        # Adiciona separadores de milhares na parte inteira
        if len(parte_inteira) > 3:
            # Inverte para facilitar inserção dos pontos
            inteira_invertida = parte_inteira[::-1]
            # Adiciona ponto a cada 3 dígitos
            com_pontos = '.'.join([inteira_invertida[i:i+3] for i in range(0, len(inteira_invertida), 3)])
            # Inverte de volta
            parte_inteira = com_pontos[::-1]
        
        return f"{parte_inteira},{parte_decimal}"
        
    except (ValueError, TypeError, AttributeError):
        return "0,00"


