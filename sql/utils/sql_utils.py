from pathlib import Path
import pandas as pd
from sqlalchemy import text

def carregar_sql(nome_arquivo_sql):
    caminho = Path(__file__).parent.parent / nome_arquivo_sql
    return caminho.read_text(encoding='utf-8')


def sql_para_dataframe(nome_arquivo_sql, conexao, params=None):
    
    """
    Executa um arquivo .sql e retorna o resultado como DataFrame.

    Parâmetros:
    - nome_arquivo_sql: str — nome do arquivo .sql (ex: 'consulta.sql')
    - conexao: conexão com o banco de dados (SQLAlchemy Engine)
    - params: dicionário de parâmetros (ex: {'CODI_EMP': 1})

    Retorna:
    - DataFrame com o resultado da query
    
    """
    sql_str = carregar_sql(nome_arquivo_sql)
    query = text(sql_str)  # trata como texto parametrizável do SQLAlchemy
    return pd.read_sql(query, con=conexao, params=params)
