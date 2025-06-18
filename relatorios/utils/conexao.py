import pyodbc

CONEXOES_DOMINIO = {
    "Banco 1": (
        "DRIVER={SQL Anywhere 17};"
        "HOST=dominio.evolucaocontabilidade.com:2638;"
        "DBN=contabil;"
        "UID=EXTERNO;"
        "PWD=123456;"
    ),
    "Banco 2": (
        "DRIVER={SQL Anywhere 17};"
        "HOST=dominio-dois.evolucaocontabilidade.com:2638;"
        "DBN=contabil;"
        "UID=EXTERNO;"
        "PWD=123456;"
    ),
    "Banco 3": (
        "DRIVER={SQL Anywhere 17};"
        "HOST=10.8.1.25:2638;"
        "DBN=contabil;"
        "UID=EXTERNO;"
        "PWD=123456;"
    ),
    "Banco 4": (
        "DRIVER={SQL Anywhere 17};"
        "HOST=10.8.1.21:2638;"
        "DBN=contabil;"
        "UID=EXTERNO;"
        "PWD=123456;"
    )
}

def conectar_dominio(banco):
    conexao = pyodbc.connect(CONEXOES_DOMINIO[banco])
    return conexao
