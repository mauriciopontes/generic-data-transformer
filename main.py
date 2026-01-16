import pandas as pd
import json

def processar_dados(caminho_input: str, caminho_config: str):
    # 1. Carga
    with open(caminho_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    df_origem = pd.read_excel(caminho_input, engine='openpyxl')
    colunas_ancora = config['colunas_ancora']
    mapeamento = config['mapeamento_segmentos']
    
    # Identificamos quais são os segmentos "específicos" (excluindo o Geral)
    segmentos_especificos = {k: v for k, v in mapeamento.items() if k != 'Geral'}
    
    lista_final = []

    for registro in df_origem.to_dict('records'):
        # --- LÓGICA DE DECISÃO DE SEGMENTO ---
        
        # Verificamos se há algum dado nos segmentos específicos
        tem_segmento_especifico = any(
            pd.notna(registro.get(cols[0])) and registro.get(cols[0]) != 0 
            for k, cols in segmentos_especificos.items()
        )

        # Definimos quais segmentos vamos processar para este ativo
        if tem_segmento_especifico:
            # Se tem segmentação de taxas, ignoramos o 'Geral'
            segmentos_para_processar = segmentos_especificos
        else:
            # Se não, usamos apenas o 'Geral'
            segmentos_para_processar = {'Geral': mapeamento['Geral']}

        # --- TRANSFORMAÇÃO ---
        for segmento, colunas_alvo in segmentos_para_processar.items():
            taxa = registro.get(colunas_alvo[0])
            grossup = registro.get(colunas_alvo[1])
            
            # Só adiciona se a taxa não for nula
            if pd.notna(taxa) and taxa != 0:
                nova_linha = {col: registro.get(col) for col in colunas_ancora}
                nova_linha.update({
                    'Segmento': segmento,
                    'Taxa': taxa,
                    'GrossUp': grossup
                })
                lista_final.append(nova_linha)

    # 4. Finalização
    df_res = pd.DataFrame(lista_final)
    
    # Formatação de data
    if 'Vencimento' in df_res.columns:
        df_res['Vencimento'] = pd.to_datetime(df_res['Vencimento']).dt.strftime('%d/%m/%Y')

    # Reordenação de colunas
    ordem = ['Ativo', 'Segmento', 'Taxa', 'GrossUp'] + [c for c in colunas_ancora if c != 'Ativo']
    return df_res[ordem]

if __name__ == "__main__":
    try:
        df_final = processar_dados(r"spreadsheets\raw_data\raw_data.xlsx", "config.json")
        df_final.to_excel(r"spreadsheets\clean_structured_data\clean_structured_data.xlsx", index=False)
        print("Processamento Concluído com Sucesso.")
    except Exception as e:
        print(f"Erro: {e}")