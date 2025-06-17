from pathlib import Path
import pandas as pd
from warnings import filterwarnings

filterwarnings("ignore", category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')

def carregar_sql(nome_arquivo_sql):
    caminho = Path(__file__).parent.parent / nome_arquivo_sql
    return caminho.read_text(encoding='utf-8')


def sql_para_dataframe(nome_arquivo_sql, conexao, params=None):
    """
    Executa um arquivo .sql e retorna o resultado como DataFrame.
    
    Parâmetros:
    - nome_arquivo_sql: str — nome do arquivo .sql (ex: 'consulta.sql')
    - conexao: conexão com o banco de dados
    - params: lista de parâmetros opcionais para substituir os ?

    Retorna:
    - DataFrame com o resultado da query
    """
    
    sql = carregar_sql(nome_arquivo_sql)
    return pd.read_sql(sql, conexao, params=params)
