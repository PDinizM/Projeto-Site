# from datetime import date

# import pandas as pd
# from sqlalchemy import and_, between, select

from relatorios.models.contabil.lancamentos import CtLancto

# from relatorios.models.contabil.lancamentos import CtLancto
from relatorios.utils.analisar_tabela import analisar_tabela, imprimir_analise_tabela
from relatorios.utils.conexao import conectar_dominio

engine = conectar_dominio("Banco 1")
resultado = analisar_tabela(model_class=CtLancto, engine=engine)

imprimir_analise_tabela(resultado)

# # Definindo as datas para o BETWEEN

# data_inicio = date(2024, 1, 1)
# data_fim = date(2024, 6, 30)

# q = (
#     select(CtContas.nome_cta)  # Seleciona o nome da conta de débito
#     .join(
#         CtLancto,
#         and_(
#             CtLancto.cdeb_lan == CtContas.codi_cta,
#             CtLancto.codi_emp == CtContas.codi_emp,
#         ),
#     )
#     .where(CtLancto.codi_emp == 1, between(CtLancto.data_lan, data_inicio, data_fim))
#     .distinct()
#     .order_by(CtContas.nome_cta)  # Ordena pelo nome da conta
# )

# tabela = pd.read_sql(q, engine)

# print(tabela)
