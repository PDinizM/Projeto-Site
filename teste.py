import time
import pandas as pd
from relatorios.utils.classificacoes import regraClassificacaoDominio, regraClassificacaoECF
from warnings import filterwarnings
from sql.utils.sql_utils import sql_para_dataframe
from relatorios.utils.conexao import conectar_dominio

conexao = conectar_dominio("Banco 1")

params = {
    'codi_emp': 623,
    'data_inicial': '2020-01-01',
    'data_final': '2024-12-01',
    'zeramento': 'S',
    'transferencia': 'N'
}

start_time = time.time()

resultadoDebitoAtual = sql_para_dataframe('dominio/balancete/normal/LancamentosDebitoNormal_Referencial.sql', conexao, params=params)
resultadoDebitoAtual = sql_para_dataframe('dominio/balancete/normal/LancamentosCreditoNormal_Referencial.sql', conexao, params=params)

end_time = time.time()
elapsed_time = end_time - start_time

print(f'Query executada em {elapsed_time:.2f} segundos')
print('foi')

