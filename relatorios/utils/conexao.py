from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

CONEXOES_DOMINIO = {
    "Banco 1": "sqlalchemy_sqlany://EXTERNO:123456@dominio.evolucaocontabilidade.com:2638/contabil",
    "Banco 2": "sqlalchemy_sqlany://EXTERNO:123456@dominio-dois.evolucaocontabilidade.com:2638/contabil",
    "Banco 3": "sqlalchemy_sqlany://EXTERNO:123456@10.8.1.25:2638/contabil",
    "Banco 4": "sqlalchemy_sqlany://EXTERNO:123456@10.8.1.21:2638/contabil"
}

def conectar_dominio(banco: str) -> Engine:
    """
    Retorna um SQLAlchemy Engine para o banco solicitado.
    """
    
    engine = create_engine(CONEXOES_DOMINIO[banco], pool_pre_ping=True)
    return engine
