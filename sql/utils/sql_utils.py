from pathlib import Path

import pandas as pd
from sqlalchemy import bindparam, text
from sqlalchemy.engine import Engine


def carregar_sql(nome_arquivo_sql: str) -> str:
    caminho = Path(__file__).parent.parent / nome_arquivo_sql
    return caminho.read_text(encoding="utf-8")


def sql_para_dataframe(
    nome_arquivo_sql: str,
    conexao: Engine,
    params: dict = None,
    params_expansiveis: dict[str, type] = None,
) -> pd.DataFrame:
    """
    Executa um arquivo .sql e retorna o resultado como DataFrame.

    Parâmetros:
    - nome_arquivo_sql: str — nome do arquivo .sql
    - conexao: Engine — conexão com o banco via SQLAlchemy
    - params: dict — parâmetros para o SQL (ex: {"CODI_EMP": 1})
    - binds_expansiveis: dict — binds que são listas, com seus tipos
      Ex: {"lista_empresas": Integer}

    Retorna:
    - DataFrame com o resultado da query
    """
    sql_str = carregar_sql(nome_arquivo_sql)
    query = text(sql_str)

    # Adiciona binds expansíveis dinamicamente
    if params_expansiveis:
        for nome_bind, tipo in params_expansiveis.items():
            query = query.bindparams(bindparam(nome_bind, expanding=True, type_=tipo))

    return pd.read_sql(query, con=conexao, params=params)
