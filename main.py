import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

def processar_dados(caminho_excel: str, caminho_config: str):
    """
    Lê um arquivo Excel e o transforma conforme as regras do JSON.
    """

    with open(caminho_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    colunas_ancora = config['colunas_ancora']
    mapeamento = config['mapeamento_segmentos']

    # 2. Ler Excel (Sem se preocupar com encoding ou separadores)
    df_origem = pd.read_excel(caminho_excel, engine='openpyxl')

    lista_final = []

    # 3. Transformação (Unpivoting)
    for _, linha in df_origem.iterrows():
        for segmento, colunas in mapeamento.items():
            # Criar dicionário da nova linha
            nova_entrada = {col: linha.get(col) for col in colunas_ancora}
            
            nova_entrada['Segmento'] = segmento
            nova_entrada['Taxa'] = linha.get(colunas[0])
            nova_entrada['GrossUp'] = linha.get(colunas[1])
            
            lista_final.append(nova_entrada)

    # 4. Criar DataFrame Resultante
    df_resultante = pd.DataFrame(lista_final)

    # Reorganizar colunas (Segmento e Taxas primeiro)
    colunas_finais = ['Ativo', 'Segmento', 'Taxa', 'GrossUp'] + \
                     [c for c in colunas_ancora if c != 'Ativo']
    
    return df_resultante[colunas_finais]

if __name__ == "__main__":
    try:
        # Caminhos dos arquivos
        INPUT = r"spreadsheets\raw_data\raw_data.xlsx"
        CONFIG = "config.json"
        OUTPUT = r"spreadsheets\clean_structured_data\clean_structured_data.xlsx"

        df_final = processar_dados(INPUT, CONFIG)

        # 5. Salvar o resultado de volta para Excel
        df_final.to_excel(OUTPUT, index=False, engine='openpyxl')
        
        print(f"Processamento concluído.")

    except Exception as e:
        print(f"Erro: {e}")