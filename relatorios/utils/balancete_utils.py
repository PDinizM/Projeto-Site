import pandas as pd
from sqlalchemy.engine import Engine

from relatorios.utils.classificacoes import (
    regraClassificacaoDominio,
    regraClassificacaoECF,
)
from sql.utils.sql_utils import sql_para_dataframe

# RELÁTORIOS DE BALANCETE

# BALANCETE ECF


def relatorioBalanceteECF(
    empresa: str,
    data_inicial: str,
    data_final: str,
    zeramento: bool,
    transferencia: bool,
    conexao: Engine,
) -> pd.DataFrame:
    zeramento_param = "S" if zeramento else "N"
    transferencia_param = "S" if transferencia else "N"

    # PEGA OS PARAMETROS E DEIXA ORGANIZADO PARA PREENCHER AS VARIAVEIS DOS .SQL

    params = {
        "codi_emp": empresa,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "zeramento": zeramento_param,
        "transferencia": transferencia_param,
    }

    ### Consultas (Resultado)

    resultadoDebitoAnterior = sql_para_dataframe(
        "dominio/balancete/ECF/DebitoAnterior.sql", conexao, params=params
    )
    resultadoCreditoAnterior = sql_para_dataframe(
        "dominio/balancete/ECF/CreditoAnterior.sql", conexao, params=params
    )
    resultadoDebitoAtual = sql_para_dataframe(
        "dominio/balancete/ECF/DebitoAtual.sql", conexao, params=params
    )
    resultadoCreditoAtual = sql_para_dataframe(
        "dominio/balancete/ECF/CreditoAtual.sql", conexao, params=params
    )
    resultadoContasECF = sql_para_dataframe(
        "dominio/balancete/ECF/contasECF.sql", conexao
    )

    # JUNTANDO OS RELÁTORIOS DE BALANCETE TUDO EM UM SÓ

    balancete = (
        resultadoContasECF.merge(resultadoDebitoAtual, on="contaLancamento", how="left")
        .merge(resultadoCreditoAtual, on="contaLancamento", how="left")
        .merge(resultadoDebitoAnterior, on="contaLancamento", how="left")
        .merge(resultadoCreditoAnterior, on="contaLancamento", how="left")
    )

    # COLOCANDO VALOR DE 0 PARA OS DEMAIS

    colunas_numericas = [
        "debitoAnterior",
        "credito_atual",
        "debito_atual",
        "creditoAnterior",
    ]
    for col in colunas_numericas:
        if col in balancete.columns:
            balancete[col] = pd.to_numeric(balancete[col], errors="coerce").fillna(0)

    # OBTENDO O SALDO ANTERIOR

    balancete["saldo_anterior"] = (
        balancete["debitoAnterior"] - balancete["creditoAnterior"]
    )

    # REMOVENDO AS COLUNAS DE ANTERIOR, POIS NÃO PRECISA MAIS DELAS

    balancete = balancete.drop(["debitoAnterior", "creditoAnterior"], axis=1)

    # COLETANDO O SALDO ATUAL

    balancete["saldo_atual"] = (
        balancete["saldo_anterior"]
        + balancete["debito_atual"]
        - balancete["credito_atual"]
    )

    # FAZENDO COM QUE AS CONTAS SINTETICAS PUXE AS INFORMAÇÕES DE SUAS RESPECTIVAS

    analiticas = balancete[balancete["tipoConta"] == "A"].copy()

    for i, linha in balancete.iterrows():
        # VERIFICA SE A CONTA É ANALITICA

        if linha["tipoConta"] == "S":
            classificacao_sintetica = linha[
                "classificacaoConta"
            ]  # PEGANDO A CLASSIFICAÇÃO DA SINTETICA
            contas_analiticas = analiticas[
                analiticas["classificacaoConta"].str.startswith(classificacao_sintetica)
            ]  # FILTRANDO PELAS ANALITICAS QUE TEM O TRECHO DA SINTETICA

            # SOMANDO AS COLUNAS

            soma_debito = contas_analiticas["debito_atual"].sum()
            soma_credito = contas_analiticas["credito_atual"].sum()
            saldo_anterior = contas_analiticas["saldo_anterior"].sum()
            saldo_atual = saldo_anterior + soma_debito - soma_credito

            # ADICIONA O RESULTADO NAS COLUNAS

            balancete.loc[i, "credito_atual"] = soma_credito
            balancete.loc[i, "debito_atual"] = soma_debito
            balancete.loc[i, "saldo_anterior"] = saldo_anterior
            balancete.loc[i, "saldo_atual"] = saldo_atual

    # REMOVENDO AS COLUNAS QUE NAO MOVIMENTARAM NADA EM NENHUMA DAS 4 COLUNAS

    balancete = balancete[
        (balancete["debito_atual"] != 0)
        | (balancete["credito_atual"] != 0)
        | (balancete["saldo_anterior"] != 0)
        | (balancete["saldo_atual"] != 0)
    ]
    balancete.sort_values(
        "classificacaoConta", inplace=True
    )  # ORDENANDO PELA CLASSIFICAÇÃO

    # Formata a Classificação para ficar igual da ECF

    balancete["classificacaoConta"] = balancete["classificacaoConta"].apply(
        regraClassificacaoECF
    )

    # ARREDONDAR PARA 2 CASAS DECIMAIS
    colunas_valores = ["saldo_anterior", "debito_atual", "credito_atual", "saldo_atual"]
    balancete[colunas_valores] = balancete[colunas_valores].round(2)

    return balancete


# BALANCETE DOMINIO


def relatorioBalanceteDominio(
    empresa,
    dataInicial,
    dataFinal,
    zeramento,
    transferencia,
    conexao,
    cruzamento_ecf=False,
):
    zeramento_param = "S" if zeramento else "N"
    transferencia_param = "S" if transferencia else "N"

    params = {
        "codi_emp": empresa,
        "data_inicial": dataInicial,
        "data_final": dataFinal,
        "zeramento": zeramento_param,
        "transferencia": transferencia_param,
    }

    ### Consultas (Resultado)

    resultadoDebitoAnterior = sql_para_dataframe(
        "dominio/balancete/normal/DebitoAnterior.sql", conexao, params=params
    )
    resultadoCreditoAnterior = sql_para_dataframe(
        "dominio/balancete/normal/CreditoAnterior.sql", conexao, params=params
    )
    resultadoDebitoAtual = sql_para_dataframe(
        "dominio/balancete/normal/DebitoAtual.sql", conexao, params=params
    )
    resultadoCreditoAtual = sql_para_dataframe(
        "dominio/balancete/normal/CreditoAtual.sql", conexao, params=params
    )
    resultadoContasDominio = sql_para_dataframe(
        "dominio/balancete/normal/contasDominio.sql", conexao, params=params
    )

    # JUNTANDO OS RELÁTORIOS DE BALANCETE TUDO EM UM SÓ

    balancete = (
        resultadoContasDominio.merge(
            resultadoDebitoAtual, on="contaLancamento", how="left"
        )
        .merge(resultadoCreditoAtual, on="contaLancamento", how="left")
        .merge(resultadoDebitoAnterior, on="contaLancamento", how="left")
        .merge(resultadoCreditoAnterior, on="contaLancamento", how="left")
    )

    # COLOCANDO VALOR DE 0 PARA OS DEMAIS

    colunas_numericas = [
        "debitoAnterior",
        "credito_atual",
        "debito_atual",
        "creditoAnterior",
    ]
    for col in colunas_numericas:
        if col in balancete.columns:
            balancete[col] = pd.to_numeric(balancete[col], errors="coerce").fillna(0)

    # OBTENDO O SALDO ANTERIOR

    balancete["saldo_anterior"] = (
        balancete["debitoAnterior"] - balancete["creditoAnterior"]
    )

    # REMOVENDO AS COLUNAS DE ANTERIOR, POIS NÃO PRECISA MAIS DELAS

    balancete = balancete.drop(["debitoAnterior", "creditoAnterior"], axis=1)

    # COLETANDO O SALDO ATUAL

    balancete["saldo_atual"] = (
        balancete["saldo_anterior"]
        + balancete["debito_atual"]
        - balancete["credito_atual"]
    )

    # FAZENDO COM QUE AS CONTAS SINTETICAS PUXE AS INFORMAÇÕES DE SUAS RESPECTIVAS ANÁLITICAS

    analiticas = balancete[balancete["tipoConta"] == "A"].copy()

    for i, linha in balancete.iterrows():
        # VERIFICA SE A CONTA É ANALITICA

        if linha["tipoConta"] == "S":
            classificacao_sintetica = linha[
                "classificacaoConta"
            ]  # PEGANDO A CLASSIFICAÇÃO DA SINTETICA
            contas_analiticas = analiticas[
                analiticas["classificacaoConta"].str.startswith(classificacao_sintetica)
            ]  # FILTRANDO PELAS ANALITICAS QUE TEM O TRECHO DA SINTETICA

            # SOMANDO AS COLUNAS

            soma_debito = contas_analiticas["debito_atual"].sum()
            soma_credito = contas_analiticas["credito_atual"].sum()
            saldo_anterior = contas_analiticas["saldo_anterior"].sum()
            saldo_atual = saldo_anterior + soma_debito - soma_credito

            # ADICIONA O RESULTADO NAS COLUNAS

            balancete.loc[i, "credito_atual"] = soma_credito
            balancete.loc[i, "debito_atual"] = soma_debito
            balancete.loc[i, "saldo_anterior"] = saldo_anterior
            balancete.loc[i, "saldo_atual"] = saldo_atual

    # REMOVENDO AS COLUNAS QUE NAO MOVIMENTARAM NADA EM NENHUMA DAS 4 COLUNAS

    balancete = balancete[
        (balancete["debito_atual"] != 0)
        | (balancete["credito_atual"] != 0)
        | (balancete["saldo_anterior"] != 0)
        | (balancete["saldo_atual"] != 0)
    ]
    balancete.sort_values(
        "classificacaoConta", inplace=True
    )  # ORDENANDO PELA CLASSIFICAÇÃO

    # Formata a Classificação para ficar igual da ECF

    balancete["classificacaoConta"] = balancete["classificacaoConta"].apply(
        regraClassificacaoDominio
    )

    # ARREDONDAR PARA 2 CASAS DECIMAIS
    colunas_valores = ["saldo_anterior", "debito_atual", "credito_atual", "saldo_atual"]
    balancete[colunas_valores] = balancete[colunas_valores].round(2)

    if cruzamento_ecf:
        ### Consultas (Resultado)

        relacao_credito_conta_normal_para_referencial = sql_para_dataframe(
            "dominio/balancete/normal/lancamentosCreditoNormal_Referencial.sql",
            conexao,
            params=params,
        )
        relacao_debito_conta_normal_para_referencial = sql_para_dataframe(
            "dominio/balancete/normal/lancamentosDebitoNormal_Referencial.sql",
            conexao,
            params=params,
        )
        resultadoContasECF = sql_para_dataframe(
            "dominio/balancete/ECF/contasECF.sql", conexao
        )

        # UNIFICA AS DUAS RELAÇÕES E REMOVE AS DUPLICATAS ENTRE ELAS

        relacao_unificada = (
            pd.concat(
                [
                    relacao_credito_conta_normal_para_referencial,
                    relacao_debito_conta_normal_para_referencial,
                ]
            )
            .drop_duplicates(["contaLancamento", "contaLancamento_ECF"])
            .reset_index(drop=True)
        )

        # RENOMEIO AS COLUNAS DO DATAFRAME DAS CONTAS ECF SE NAO VAI DAR DIVERGENCIA DE NOME QUANDO MESCLAR COM O BALANCETE NORMAL.

        resultadoContasECF.rename(
            columns={
                "contaLancamento": "contaLancamento_ECF",
                "classificacaoConta": "classificacaoConta_ECF",
                "descricaoConta": "descricaoConta_ECF",
                "tipoConta": "tipoConta_ECF",
            },
            inplace=True,
        )

        # PUXA O NOME DA CONTA E A CLASSIFICAÇÃO ECF (LEFT JOIN COM resultadoContasECF)

        relacao_com_classificacao = relacao_unificada.merge(
            resultadoContasECF[
                ["contaLancamento_ECF", "classificacaoConta_ECF", "descricaoConta_ECF"]
            ],
            on="contaLancamento_ECF",
            how="left",
        ).drop(columns=["contaLancamento_ECF"])

        # TROCO NaN POR '' PARA FACILITAR NA HORA DE AJUDAR NAS LOGICAS QUE SERÃO APLICADAS NO RESTANTE DO CODIGO

        relacao_com_classificacao = relacao_com_classificacao.fillna("")

        # AGRUPO O DATAFRAME UTILIZANDO CONTALANCAMENTO COMO A LOGICA DE AGRUPAMENTO, ELES SÃO AGRUPADOS EM UMA LISTA

        agrupado = (
            relacao_com_classificacao.groupby("contaLancamento")
            .agg({"descricaoConta_ECF": list, "classificacaoConta_ECF": list})
            .reset_index()
        )

        # CRIA A COLUNA SEM REFERENCIAL COM BASE A CLASSIFICAÇÃO TER UM ELEMENTO VAZIO NA LISTA

        agrupado[
            ["descricaoConta_ECF", "classificacaoConta_ECF", "Sem_Referencial"]
        ] = agrupado.apply(
            lambda row: pd.Series(
                [
                    [x for x in row["descricaoConta_ECF"] if x != ""],
                    [x for x in row["classificacaoConta_ECF"] if x != ""],
                    "S" if "" in row["classificacaoConta_ECF"] else "N",
                ]
            ),
            axis=1,
        )

        # COLOCANDO FORMATAÇÃO DA CLASSIFICAÇÃO REFERENCIAL

        agrupado["classificacaoConta_ECF"] = agrupado["classificacaoConta_ECF"].apply(
            lambda lst: [regraClassificacaoECF(x) for x in lst] if lst else lst
        )

        # SE HOUVER APENAS UM ELEMENTO ELE IRA TIRAR O ESTILO DA LISTA E APLICAR O VALOR QUE ESTA LA NA CELULA, DESSA MANEIRA FICANDO MAIS ELEGANTE

        agrupado["classificacaoConta_ECF"] = agrupado["classificacaoConta_ECF"].apply(
            lambda l: "" if not l else (l[0] if len(l) == 1 else l)
        )

        agrupado["descricaoConta_ECF"] = agrupado["descricaoConta_ECF"].apply(
            lambda l: "" if not l else (l[0] if len(l) == 1 else l)
        )

        agrupado["Qtd_Ref"] = (
            agrupado["classificacaoConta_ECF"]
            .apply(lambda x: len(x) if isinstance(x, list) else 1)
            .astype(str)
        )

        # FAÇO UM JOIN COM TODA A ANALISE QUE FOI FEITA E AS TRATIVAS DE DADOS COM O BALANCETE

        balancete_com_ref = pd.merge(
            balancete, agrupado, on="contaLancamento", how="left"
        )

        # FILTRO APENAS AS ANALITICAS E AS QUE HOUVERAM MOVIMENTAÇÃO PARA QUE A ANALISE POSSA CONTINUAR

        balancete_com_ref_analiticas = balancete_com_ref[
            (balancete_com_ref["tipoConta"] == "A")
            & (
                (balancete_com_ref["debito_atual"] > 0)
                | (balancete_com_ref["credito_atual"] > 0)
            )
        ]

        balancete_com_ref_analiticas = balancete_com_ref_analiticas.copy()

        balancete_com_ref_analiticas["DC S.Ant."] = balancete_com_ref_analiticas[
            "saldo_anterior"
        ].apply(lambda x: "C" if x > 0 else ("D" if x < 0 else ""))

        balancete_com_ref_analiticas["DC S.Atual"] = balancete_com_ref_analiticas[
            "saldo_atual"
        ].apply(lambda x: "C" if x > 0 else ("D" if x < 0 else ""))

        # Transformar os valores dos saldos em absolutos (positivos)
        balancete_com_ref_analiticas["saldo_anterior"] = balancete_com_ref_analiticas[
            "saldo_anterior"
        ].abs()
        balancete_com_ref_analiticas["saldo_atual"] = balancete_com_ref_analiticas[
            "saldo_atual"
        ].abs()

        balancete_com_ref_analiticas = balancete_com_ref_analiticas.rename(
            columns={
                "contaLancamento": "Código",
                "classificacaoConta": "Classificação",
                "descricaoConta": "Descrição da Conta",
                "tipoConta": "Tipo",
                "saldo_anterior": "Saldo Anterior",
                "debito_atual": "Débito",
                "credito_atual": "Crédito",
                "saldo_atual": "Saldo Atual",
                "classificacaoConta_ECF": "Classificação ECF",
                "descricaoConta_ECF": "Descrição da Conta ECF",
                "Qtd_Ref": "QTD Referencial",
                "Sem_Referencial": "Sem Referencial",
            }
        )

        balancete_com_ref_analiticas = balancete_com_ref_analiticas[
            [
                "Código",
                "Classificação",
                "Descrição da Conta",
                "Tipo",
                "Saldo Anterior",
                "DC S.Ant.",
                "Débito",
                "Crédito",
                "Saldo Atual",
                "DC S.Atual",
                "Classificação ECF",
                "Descrição da Conta ECF",
                "QTD Referencial",
                "Sem Referencial",
            ]
        ]

        return balancete_com_ref_analiticas

    return balancete


def gerar_balancete(
    tipo: str,
    empresa: str,
    data_inicial: str,
    data_final: str,
    conexao: Engine,
    zeramento: bool,
    transferencia: bool,
    cruzamento_ecf: bool,
) -> pd.DataFrame:
    if tipo == "plano_referencial":
        return relatorioBalanceteECF(
            empresa, data_inicial, data_final, zeramento, transferencia, conexao
        )
    else:
        return relatorioBalanceteDominio(
            empresa,
            data_inicial,
            data_final,
            zeramento,
            transferencia,
            conexao,
            cruzamento_ecf,
        )
