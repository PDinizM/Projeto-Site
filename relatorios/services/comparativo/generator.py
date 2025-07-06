from __future__ import annotations

import pandas as pd

from relatorios.utils.classificacoes import regraClassificacaoDominio
from relatorios.utils.competencias import obter_intervalo_meses
from sql.utils.sql_utils import sql_para_dataframe

from .context import ComparativoContext, ComparativoEmptyError


class Comparativo:
    """
    Classe para geração de comparativos contábeis.

    """

    @staticmethod
    def gerar(params: ComparativoContext) -> pd.DataFrame:
        """
        Gera um comparativo contábil no formato especificado, para uma ou mais empresas.

        Parâmetros:
        -----------
        empresas : str ou List[str]
            Código(s) da(s) empresa(s). Pode ser uma string única ou lista de strings.
        data_inicial : date
            Data inicial no formato 'YYYY-MM-DD'
        data_final : date
            Data final no formato 'YYYY-MM-DD'
        conexao : Engine
            Conexão com o banco de dados SQLAlchemy
        zeramento : bool, optional
            Indica se deve incluir lançamentos de zeramento (padrão: False)
        transferencia : bool, optional
            Indica se deve incluir lançamentos de transferência (padrão: False)

        Retorna:
        --------
        pd.DataFrame ou List[pd.DataFrame]
            DataFrame(s) com o(s) compartivo(s) gerado(s)
        """
        lista_codigos_empresas = (
            [params.empresas]
            if isinstance(params.empresas, str)
            else params.empresas.copy()
        )

        lista_comparativos: list[pd.DataFrame] = []

        for codigo_empresa in lista_codigos_empresas:
            df_comparativo = Comparativo._gerar_empresa(codigo_empresa, params)
            if df_comparativo.empty:
                continue
            df_comparativo.insert(0, "Cód. Empresa", codigo_empresa)
            lista_comparativos.append(df_comparativo)

        if not lista_comparativos:
            raise ComparativoEmptyError()

        return pd.concat(lista_comparativos, ignore_index=True)

    @staticmethod
    def _gerar_empresa(empresa: str, params: ComparativoContext) -> pd.DataFrame:
        zeramento_param = "S" if params.zeramento else "N"
        transferencia_param = "S" if params.transferencia else "N"
        data_inicial_str = params.data_inicial.strftime("%Y-%m-%d")
        data_final_str = params.data_final.strftime("%Y-%m-%d")

        sql_params = {
            "codi_emp": empresa,
            "data_inicial": data_inicial_str,
            "data_final": data_final_str,
            "zeramento": zeramento_param,
            "transferencia": transferencia_param,
        }

        contas = sql_para_dataframe(
            "dominio/comparativo/contasDominio.sql",
            params.conexao,
            params=sql_params,
        )

        comparativo = contas.copy()

        if not params.saldo_anterior:
            resultadoDebitoAnterior = sql_para_dataframe(
                "dominio/comparativo/DebitoAnterior.sql",
                params.conexao,
                params=sql_params,
            )
            resultadoCreditoAnterior = sql_para_dataframe(
                "dominio/comparativo/CreditoAnterior.sql",
                params.conexao,
                params=sql_params,
            )
            comparativo = comparativo.merge(
                resultadoDebitoAnterior, on="conta_lancamento", how="left"
            ).merge(resultadoCreditoAnterior, on="conta_lancamento", how="left")

            comparativo.fillna(0, inplace=True)

            comparativo["saldo_anterior"] = (
                comparativo["debito_anterior"] - comparativo["credito_anterior"]
            )
            comparativo.drop(
                ["debito_anterior", "credito_anterior"], axis=1, inplace=True
            )

        colunas_competencia: list[str] = []
        for competencia, data_inicial, data_final in obter_intervalo_meses(
            params.data_inicial, params.data_final
        ):
            colunas_competencia.append(competencia)

            sql_params.update({"data_inicial": data_inicial, "data_final": data_final})

            cred_mes = sql_para_dataframe(
                "dominio/comparativo/CreditoAtual.sql",
                params.conexao,
                params=sql_params,
            )
            deb_mes = sql_para_dataframe(
                "dominio/comparativo/DebitoAtual.sql",
                params.conexao,
                params=sql_params,
            )

            mensal = cred_mes.merge(deb_mes, on="conta_lancamento", how="outer")
            mensal[competencia] = mensal["debito_atual"].sub(
                mensal["credito_atual"], fill_value=0
            )
            comparativo = comparativo.merge(
                mensal[["conta_lancamento", competencia]],
                on="conta_lancamento",
                how="left",
            )

        # -----------------------------------------------------------------
        # Preenchimento de NaN ➜ 0
        # -----------------------------------------------------------------
        comparativo.fillna(0, inplace=True)

        # -----------------------------------------------------------------
        # Sintéticas (Somatório)
        # -----------------------------------------------------------------
        analiticas = comparativo[comparativo["tipo_conta"] == "A"]
        for idx, row in comparativo.iterrows():
            if row["tipo_conta"] == "S":
                prefixo = row["classificacao_conta"]
                subset = analiticas[
                    analiticas["classificacao_conta"].str.startswith(prefixo)
                ]
                for col in colunas_competencia + (
                    ["saldo_anterior"] if not params.saldo_anterior else []
                ):
                    comparativo.loc[idx, col] = subset[col].sum()

        # -----------------------------------------------------------------
        # Acumulação de saldo / cálculo de saldo_acumulado
        # -----------------------------------------------------------------
        if not params.saldo_anterior:
            comparativo[colunas_competencia] = comparativo[colunas_competencia].cumsum(
                axis=1
            )
        elif params.saldo_acumulado:
            comparativo["saldo_acumulado"] = comparativo[colunas_competencia].sum(
                axis=1
            )

        # -----------------------------------------------------------------
        # Limpeza: remove linhas sem movimento
        # -----------------------------------------------------------------
        col_ver = colunas_competencia + (
            ["saldo_anterior"] if not params.saldo_anterior else []
        )
        comparativo = comparativo.loc[~(comparativo[col_ver] == 0).all(axis=1)]

        # -----------------------------------------------------------------
        # Ordenação + formatação
        # -----------------------------------------------------------------
        comparativo.sort_values("classificacao_conta", inplace=True)
        comparativo["classificacao_conta"] = comparativo["classificacao_conta"].apply(
            regraClassificacaoDominio
        )
        comparativo[col_ver] = comparativo[col_ver].round(2)
        return comparativo.reset_index(drop=True)
