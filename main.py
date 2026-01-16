import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any

def carregar_configuracao(caminho_config: str) -> Dict[str, Any]:
    """Carrega as definições de colunas e mapeamentos de um arquivo JSON."""
    path = Path(caminho_config)
    if not path.exists():
        raise FileNotFoundError(f"Configuração não encontrada em: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def transformar_dados(caminho_entrada: str, config: Dict[str, Any]) -> pd.DataFrame:
    """Transforma os dados baseando-se no dicionário de configuração."""
    df_origem = pd.read_csv(caminho_entrada)
    colunas_ancora = config['colunas_ancora']
    mapeamento = config['mapeamento_segmentos']
    
    lista_final = []

    for _, linha in df_origem.iterrows():
        for segmento, colunas in mapeamento.items():
            # Construção da linha usando dictionary comprehension
            nova_entrada = {col: linha[col] for col in colunas_ancora}
            
            nova_entrada['Segmento'] = segmento
            nova_entrada['Taxa'] = linha.get(colunas[0])
            nova_entrada['GrossUp'] = linha.get(colunas[1])
            
            lista_final.append(nova_entrada)

    df_res = pd.DataFrame(lista_final)
    
    # Organização das colunas para o output
    ordem = ['Ativo', 'Segmento', 'Taxa', 'GrossUp'] + [c for c in colunas_ancora if c != 'Ativo']
    return df_res[ordem]

if __name__ == "__main__":
    try:
        # 1. Setup de caminhos
        ARQUIVO_INPUT = "Estruturação de Dados - Boletim.xlsx - Estrestrutura Atual .csv"
        ARQUIVO_CONFIG = "config.json"
        
        # 2. Execução
        config = carregar_configuracao(ARQUIVO_CONFIG)
        df_final = transformar_dados(ARQUIVO_INPUT, config)
        
        # 3. Exportação
        df_final.to_csv("dados_transformados_final.csv", index=False)
        print("✔ Processamento concluído via configuração JSON.")
        
    except Exception as e:
        print(f"✖ Falha na execução: {e}")