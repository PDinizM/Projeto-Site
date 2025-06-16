import pandas as pd
from relatorios.utils.classificacoes import regraClassificacaoDominio, regraClassificacaoECF
from warnings import filterwarnings

filterwarnings("ignore", category=UserWarning, message='.*pandas only supports SQLAlchemy connectable.*')

# RELÁTORIOS DE BALANCETE

# BALANCETE ECF

def relatorioBalanceteECF(empresa, dataInicial, dataFinal, zeramento, transferencia, conexao):

    ### Consultas (Código SQL)

    sqlConsultaDebitoAtual = f"""
        SELECT
            contaLancamento = CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO,
            debitoAtual = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.CTLANCTO_SPED_ECF_GERAL
            
        INNER JOIN bethadba.ctlancto ON 
            ctlancto.codi_emp = CTLANCTO_SPED_ECF_GERAL.CODI_EMP AND
            ctlancto.nume_lan = CTLANCTO_SPED_ECF_GERAL.NUME_LAN
            
        WHERE
            CTLANCTO_SPED_ECF_GERAL.CODI_EMP = {empresa} AND
            CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO <> 0 AND
            ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
            ('{zeramento}' = 'N' OR ('{zeramento}' = 'S' AND ctlancto.orig_lan <> 2)) AND
            ('{transferencia}' = 'N' OR ('{transferencia}' = 'S' AND ctlancto.orig_lan <> 34))
            
        GROUP BY
            contaLancamento
        """
    sqlConsultaCreditoAtual = f"""
        SELECT
            contaLancamento = CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO,
            creditoAtual = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.CTLANCTO_SPED_ECF_GERAL
            
        INNER JOIN bethadba.ctlancto ON 
            ctlancto.codi_emp = CTLANCTO_SPED_ECF_GERAL.CODI_EMP AND
            ctlancto.nume_lan = CTLANCTO_SPED_ECF_GERAL.NUME_LAN
            
        WHERE
            CTLANCTO_SPED_ECF_GERAL.CODI_EMP = {empresa} AND
            CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO <> 0 AND
            ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
            ('{zeramento}' = 'N' OR ('{zeramento}' = 'S' AND ctlancto.orig_lan <> 2)) AND
            ('{transferencia}' = 'N' OR ('{transferencia}' = 'S' AND ctlancto.orig_lan <> 34))
            
        GROUP BY
            contaLancamento
    """
    sqlConsultaCreditoAnterior = f"""
        SELECT
            contaLancamento = CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO,
            creditoAnterior = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.CTLANCTO_SPED_ECF_GERAL
            
        INNER JOIN bethadba.ctlancto ON 
            ctlancto.codi_emp = CTLANCTO_SPED_ECF_GERAL.CODI_EMP AND
            ctlancto.nume_lan = CTLANCTO_SPED_ECF_GERAL.NUME_LAN
            
        WHERE
            CTLANCTO_SPED_ECF_GERAL.CODI_EMP = {empresa} AND
            CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO <> 0 AND
            ctlancto.data_lan < '{dataInicial}' 
            
        GROUP BY
            contaLancamento
    """
    sqlConsultaDebitoAnterior = f"""
        SELECT
            contaLancamento = CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO,
            debitoAnterior = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.CTLANCTO_SPED_ECF_GERAL
            
        INNER JOIN bethadba.ctlancto ON 
            ctlancto.codi_emp = CTLANCTO_SPED_ECF_GERAL.CODI_EMP AND
            ctlancto.nume_lan = CTLANCTO_SPED_ECF_GERAL.NUME_LAN
            
        WHERE
            CTLANCTO_SPED_ECF_GERAL.CODI_EMP = {empresa} AND
            CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO <> 0 AND
            ctlancto.data_lan < '{dataInicial}'
            
        GROUP BY
            contaLancamento
    """
    sqlContasECF = """
    SELECT
        contaLancamento = bethadba.CTCONTAS_SPED_ECF_GERAL.CODIGO_CTA_SPED_ECF_GERAL,
        classificacaoConta = bethadba.CTCONTAS_SPED_ECF_GERAL.CLASSIFICACAO_SPED_ECF_GERAL,
        descricaoConta = bethadba.CTCONTAS_SPED_ECF_GERAL.DESCRICAO,
        tipoConta = bethadba.CTCONTAS_SPED_ECF_GERAL.TIPO 
    FROM
        bethadba.CTCONTAS_SPED_ECF_GERAL 
    """

    ### Consultas (Resultado)

    resultadoDebitoAnterior = pd.read_sql(sqlConsultaDebitoAnterior, conexao)
    resultadoCreditoAnterior = pd.read_sql(sqlConsultaCreditoAnterior, conexao)
    resultadoDebitoAtual = pd.read_sql(sqlConsultaDebitoAtual, conexao)
    resultadoCreditoAtual = pd.read_sql(sqlConsultaCreditoAtual, conexao)
    resultadoContasECF = pd.read_sql(sqlContasECF, conexao)

    # ARMAZENANDO OS RELATORIOS

    relatorio = [resultadoDebitoAnterior, resultadoCreditoAnterior, resultadoDebitoAtual, resultadoCreditoAtual, resultadoContasECF]

    # JUNTANDO OS RELÁTORIOS DE BALANCETE TUDO EM UM SÓ

    balancete = relatorio[4].merge(relatorio[2], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[3], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[0], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[1], on="contaLancamento", how="left")


    # COLOCANDO VALOR DE 0 PARA OS DEMAIS

    balancete.fillna(0, inplace=True)

    # OBTENDO O SALDO ANTERIOR

    balancete['Saldo Anterior'] = balancete['debitoAnterior'] - balancete['creditoAnterior']

    # REMOVENDO AS COLUNAS DE ANTERIOR, POIS NÃO PRECISA MAIS DELAS

    balancete = balancete.drop(['debitoAnterior', 'creditoAnterior'], axis=1)

    # COLETANDO O SALDO ATUAL

    balancete['Saldo Atual'] = balancete['Saldo Anterior'] + balancete['debitoAtual'] - balancete['creditoAtual']

    # FAZENDO COM QUE AS CONTAS SINTETICAS PUXE AS INFORMAÇÕES DE SUAS RESPECTIVAS ANÁLITICAS

    for i, linha in balancete.iterrows():

        # VERIFICA SE A CONTA É ANALITICA

        if linha['tipoConta'] == 'S':
            classificacao_sintetica = linha['classificacaoConta'] # PEGANDO A CLASSIFICAÇÃO DA SINTETICA
            contas_analiticas = balancete[(balancete['classificacaoConta'].str.startswith(classificacao_sintetica)) & (balancete['tipoConta'] == 'A')] # FILTRANDO PELAS ANALITICAS QUE TEM O TRECHO DA SINTETICA
            
            # SOMANDO AS COLUNAS 

            soma_debito = contas_analiticas['debitoAtual'].sum() 
            soma_credito = contas_analiticas['creditoAtual'].sum()
            saldo_anterior = contas_analiticas['Saldo Anterior'].sum()

            # ADICIONA O RESULTADO NAS COLUNAS 

            balancete.loc[i, 'creditoAtual'] = soma_credito
            balancete.loc[i, 'debitoAtual'] = soma_debito
            balancete.loc[i, 'Saldo Anterior'] = saldo_anterior
            balancete.loc[i, 'Saldo Atual'] = saldo_anterior + soma_debito - soma_credito

    # REMOVENDO AS COLUNAS QUE NAO MOVIMENTARAM NADA EM NENHUMA DAS 4 COLUNAS
    balancete = balancete[(balancete['debitoAtual'] != 0) | (balancete['creditoAtual'] != 0) | (balancete['Saldo Anterior'] != 0) | (balancete['Saldo Atual'] != 0)]
    balancete.sort_values('classificacaoConta', inplace=True) # ORDENANDO PELA CLASSIFICAÇÃO

    # Formata a Classificação para ficar igual da ECF

    balancete['classificacaoConta'] = balancete['classificacaoConta'].apply(regraClassificacaoECF)

    # COLOCANDO NA ORDEM O BALANCETE

    balancete = balancete.reindex(columns=['contaLancamento', 'classificacaoConta', 'descricaoConta', 'tipoConta', 'Saldo Anterior', 'debitoAtual', 'creditoAtual', 'Saldo Atual'])

    return balancete

# BALANCETE DOMINIO

def relatorioBalanceteDominio(empresa, dataInicial, dataFinal, zeramento, transferencia, conexao, cruzamento_ecf='N'):
    
    ### Consultas (Código SQL)

    sqlConsultaDebitoAtual = f"""
        SELECT
            contaLancamento = bethadba.ctlancto.cdeb_lan,
            debitoAtual = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.ctlancto
            
        WHERE
            bethadba.ctlancto.codi_emp = {empresa} AND
            bethadba.ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
            bethadba.ctlancto.cdeb_lan <> 0 AND
            ('{zeramento}' = 'N' OR ('{zeramento}' = 'S' AND ctlancto.orig_lan <> 2)) AND
            ('{transferencia}' = 'N' OR ('{transferencia}' = 'S' AND ctlancto.orig_lan <> 34))
        
        GROUP BY
            contaLancamento

        """
    sqlConsultaCreditoAtual = f"""
        SELECT
            contaLancamento = bethadba.ctlancto.ccre_lan,
            creditoAtual = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.ctlancto
            
        WHERE
            bethadba.ctlancto.codi_emp = {empresa} AND
            bethadba.ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
            bethadba.ctlancto.ccre_lan <> 0 AND
            ('{zeramento}' = 'N' OR ('{zeramento}' = 'S' AND ctlancto.orig_lan <> 2)) AND
            ('{transferencia}' = 'N' OR ('{transferencia}' = 'S' AND ctlancto.orig_lan <> 34))
        
        GROUP BY
            contaLancamento
    """
    sqlConsultaCreditoAnterior = f"""
        SELECT
            contaLancamento = bethadba.ctlancto.ccre_lan,
            creditoAnterior = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.ctlancto
            
        WHERE
            bethadba.ctlancto.codi_emp = {empresa} AND
            bethadba.ctlancto.data_lan < '{dataInicial}' AND
            bethadba.ctlancto.ccre_lan <> 0 
        
        GROUP BY
            contaLancamento
    """
    sqlConsultaDebitoAnterior = f"""
        SELECT
            contaLancamento = bethadba.ctlancto.cdeb_lan,
            debitoAnterior = SUM(bethadba.ctlancto.vlor_lan)
        FROM
            bethadba.ctlancto
            
        WHERE
            bethadba.ctlancto.codi_emp = {empresa} AND
            bethadba.ctlancto.data_lan < '{dataInicial}' AND
            bethadba.ctlancto.cdeb_lan <> 0 
        
        GROUP BY
            contaLancamento
    """
    sqlContasDominio = f"""
        SELECT
            contaLancamento = bethadba.ctcontas.codi_cta,
            classificacaoConta = bethadba.ctcontas.clas_cta,
            descricaoConta = bethadba.ctcontas.nome_cta,
            tipoConta = bethadba.ctcontas.tipo_cta  
        FROM
            bethadba.ctcontas
            
        WHERE
            bethadba.ctcontas.codi_emp = {empresa}
    """

    ### Consultas (Resultado)

    resultadoDebitoAnterior = pd.read_sql(sqlConsultaDebitoAnterior, conexao)
    resultadoCreditoAnterior = pd.read_sql(sqlConsultaCreditoAnterior, conexao)
    resultadoDebitoAtual = pd.read_sql(sqlConsultaDebitoAtual, conexao)
    resultadoCreditoAtual = pd.read_sql(sqlConsultaCreditoAtual, conexao)
    resultadoContasDominio = pd.read_sql(sqlContasDominio, conexao)

    # ARMAZENANDO OS RELATORIOS

    relatorio = [resultadoDebitoAnterior, resultadoCreditoAnterior, resultadoDebitoAtual, resultadoCreditoAtual, resultadoContasDominio]

    # JUNTANDO OS RELÁTORIOS DE BALANCETE TUDO EM UM SÓ

    balancete = relatorio[4].merge(relatorio[2], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[3], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[0], on="contaLancamento", how="left")
    balancete = balancete.merge(relatorio[1], on="contaLancamento", how="left")


    # COLOCANDO VALOR DE 0 PARA OS DEMAIS

    balancete.fillna(0, inplace=True)

    # OBTENDO O SALDO ANTERIOR

    balancete['Saldo Anterior'] = balancete['debitoAnterior'] - balancete['creditoAnterior']

    # REMOVENDO AS COLUNAS DE ANTERIOR, POIS NÃO PRECISA MAIS DELAS

    balancete = balancete.drop(['debitoAnterior', 'creditoAnterior'], axis=1)

    # COLETANDO O SALDO ATUAL

    balancete['Saldo Atual'] = balancete['Saldo Anterior'] + balancete['debitoAtual'] - balancete['creditoAtual']

    # FAZENDO COM QUE AS CONTAS SINTETICAS PUXE AS INFORMAÇÕES DE SUAS RESPECTIVAS ANÁLITICAS

    for i, linha in balancete.iterrows():

        # VERIFICA SE A CONTA É ANALITICA

        if linha['tipoConta'] == 'S':
            classificacao_sintetica = linha['classificacaoConta'] # PEGANDO A CLASSIFICAÇÃO DA SINTETICA
            contas_analiticas = balancete[(balancete['classificacaoConta'].str.startswith(classificacao_sintetica)) & (balancete['tipoConta'] == 'A')] # FILTRANDO PELAS ANALITICAS QUE TEM O TRECHO DA SINTETICA
            
            # SOMANDO AS COLUNAS 

            soma_debito = contas_analiticas['debitoAtual'].sum() 
            soma_credito = contas_analiticas['creditoAtual'].sum()
            saldo_anterior = contas_analiticas['Saldo Anterior'].sum()

            # ADICIONA O RESULTADO NAS COLUNAS 

            balancete.loc[i, 'creditoAtual'] = soma_credito
            balancete.loc[i, 'debitoAtual'] = soma_debito
            balancete.loc[i, 'Saldo Anterior'] = saldo_anterior
            balancete.loc[i, 'Saldo Atual'] = saldo_anterior + soma_debito - soma_credito

    # REMOVENDO AS COLUNAS QUE NAO MOVIMENTARAM NADA EM NENHUMA DAS 4 COLUNAS

    balancete = balancete[(balancete['debitoAtual'] != 0) | (balancete['creditoAtual'] != 0) | (balancete['Saldo Anterior'] != 0) | (balancete['Saldo Atual'] != 0)]
    balancete.sort_values('classificacaoConta', inplace=True) # ORDENANDO PELA CLASSIFICAÇÃO

    # Formata a Classificação para ficar igual da ECF

    balancete['classificacaoConta'] = balancete['classificacaoConta'].apply(regraClassificacaoDominio)
    
    # ARREDONDAR PARA 2 CASAS DECIMAIS
    colunas_valores = ['Saldo Anterior', 'debitoAtual', 'creditoAtual', 'Saldo Atual']
    balancete[colunas_valores] = balancete[colunas_valores].round(2)

    # COLOCANDO NA ORDEM O BALANCETE

    balancete = balancete.reindex(columns=['contaLancamento', 'classificacaoConta', 'descricaoConta', 'tipoConta', 'Saldo Anterior', 'debitoAtual', 'creditoAtual', 'Saldo Atual'])

    if cruzamento_ecf == 'S':

        sqlLancamentosRef = f"""
            SELECT  *
            FROM 
            (
                SELECT DISTINCT 
                    Conta_Normal = bethadba.ctlancto.cdeb_lan,
                    Classificacao_Referencial = bethadba.CTCONTAS_SPED_ECF_GERAL.CLASSIFICACAO_SPED_ECF_GERAL,
                    Conta_Referencial = ISNULL(bethadba.CTCONTAS_SPED_ECF_GERAL.DESCRICAO, 'SEM REFERENCIAL')
                FROM
                    bethadba.ctlancto
                    
                LEFT JOIN bethadba.CTLANCTO_SPED_ECF_GERAL ON
                    bethadba.CTLANCTO_SPED_ECF_GERAL.codi_emp = bethadba.ctlancto.codi_emp AND
                    bethadba.CTLANCTO_SPED_ECF_GERAL.nume_lan = bethadba.ctlancto.nume_lan  AND 
                    bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO <> 0
                    
                LEFT JOIN bethadba.CTCONTAS_SPED_ECF_GERAL ON
                    bethadba.CTCONTAS_SPED_ECF_GERAL.CODIGO_CTA_SPED_ECF_GERAL = bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_DEBITO
                    
                WHERE
                    bethadba.ctlancto.codi_emp = {empresa} AND
                    bethadba.ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
                    bethadba.ctlancto.cdeb_lan <> 0
                    
                UNION
                
                SELECT DISTINCT 
                    Conta_Normal = bethadba.ctlancto.ccre_lan,
                    Classificacao_Referencial = bethadba.CTCONTAS_SPED_ECF_GERAL.CLASSIFICACAO_SPED_ECF_GERAL,
                    Conta_Referencial = ISNULL(bethadba.CTCONTAS_SPED_ECF_GERAL.DESCRICAO, 'SEM REFERENCIAL')
                FROM
                    bethadba.ctlancto
                    
                LEFT JOIN bethadba.CTLANCTO_SPED_ECF_GERAL ON
                    bethadba.CTLANCTO_SPED_ECF_GERAL.codi_emp = bethadba.ctlancto.codi_emp AND
                    bethadba.CTLANCTO_SPED_ECF_GERAL.nume_lan = bethadba.ctlancto.nume_lan AND 
                    bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO <> 0
                    
                LEFT JOIN bethadba.CTCONTAS_SPED_ECF_GERAL ON
                    bethadba.CTCONTAS_SPED_ECF_GERAL.CODIGO_CTA_SPED_ECF_GERAL = bethadba.CTLANCTO_SPED_ECF_GERAL.CONTA_CREDITO
                    
                WHERE
                    bethadba.ctlancto.codi_emp = {empresa} AND
                    bethadba.ctlancto.data_lan BETWEEN '{dataInicial}' AND '{dataFinal}' AND
                    bethadba.ctlancto.ccre_lan <> 0
            ) AS Lancamentos_REF
            """

            ### Consultas (Resultado)

        resultadoLancamentosRef = pd.read_sql(sqlLancamentosRef, conexao)

        # Agrupar e criar lista de conta referencial

        agrupado = resultadoLancamentosRef.groupby('Conta_Normal')[['Classificacao_Referencial', 'Conta_Referencial']].agg(list).reset_index()

        # Adicionar a coluna QTD
        agrupado['QTD'] = agrupado['Conta_Referencial'].apply(len)

        # Substituir listas com um único elemento pelo próprio valor
        agrupado['Conta_Referencial'] = agrupado['Conta_Referencial'].apply(
            lambda x: x[0] if len(x) == 1 else x
        )

        agrupado['Classificacao_Referencial'] = agrupado['Classificacao_Referencial'].apply(
            lambda x: x[0] if len(x) == 1 else x
        )

        agrupado['Classificacao_Referencial'] = agrupado['Classificacao_Referencial'].apply(
        lambda x: regraClassificacaoECF(x) if not isinstance(x, list) else x
        )

        # Renomear coluna para permitir merge com balancete
        agrupado = agrupado.rename(columns={'Conta_Normal': 'contaLancamento'})

        # Merge com o balancete
        balancete_com_ref = pd.merge(balancete, agrupado, on='contaLancamento', how='left')

        balancete_com_ref["Sem Referencial"] = balancete_com_ref["Conta_Referencial"].apply(
            lambda x: "S" if "SEM REFERENCIAL" in str(x).upper() else "N"
        )

        balancete_com_ref_analiticas = balancete_com_ref[
            (balancete_com_ref['tipoConta'] == 'A') &
            (
                (balancete_com_ref['debitoAtual'] > 0) |
                (balancete_com_ref['creditoAtual'] > 0)
            )
        ]

        return balancete_com_ref_analiticas
        

    return balancete