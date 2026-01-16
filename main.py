import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any

def processar_dados(caminho_input: str, caminho_config: str) -> pd.DataFrame:

    with open(caminho_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    df_origem = pd.read_excel(caminho_input, engine='openpyxl')
    df_origem.columns = [c.strip() for c in df_origem.columns]
    
    colunas_ancora = config['colunas_ancora']
    mapeamento = config['mapeamento_segmentos']
    
    lista_final = []

    for registro in df_origem.to_dict('records'):
        for segmento, colunas_alvo in mapeamento.items():
            taxa = registro.get(colunas_alvo[0])
            grossup = registro.get(colunas_alvo[1])
            
            # Lógica de Filtragem: Só adiciona se houver taxa disponível
            if pd.notna(taxa) and taxa != 0:
                nova_linha = {col: registro.get(col) for col in colunas_ancora}
                nova_linha.update({
                    'Segmento': segmento,
                    'Taxa': taxa,
                    'GrossUp': grossup
                })
                lista_final.append(nova_linha)

    df_res = pd.DataFrame(lista_final)
    
    # Formata a coluna vencimento
    if 'Vencimento' in df_res.columns:
        df_res['Vencimento'] = pd.to_datetime(df_res['Vencimento']).dt.strftime('%d/%m/%Y')

    # Reordena as colunas
    ordem = ['Ativo', 'Segmento', 'Taxa', 'GrossUp'] + [c for c in colunas_ancora if c != 'Ativo']
    return df_res[ordem]

if __name__ == "__main__":
    raw_data = r'spreadsheets\raw_data\raw_data.xlsx'
    try:
        df_clean = processar_dados(raw_data, "config.json")
        df_clean.to_excel(r"spreadsheets\clean_structured_data\clean_structured_data.xlsx", index=False)
        print("Processamento concluído com sucesso.")
    except Exception as e:
        print(f"Erro: {e}")