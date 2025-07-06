from dataclasses import dataclass, field
from datetime import date
from typing import List, Literal, Optional, Union

import pandas as pd
from django.http import HttpRequest
from sqlalchemy.engine import Engine

from relatorios.forms.base import BalanceteForm
from relatorios.utils.classificacoes import (
    regraClassificacaoDominio,
    regraClassificacaoECF,
)
from sql.utils.sql_utils import sql_para_dataframe


@dataclass
class BalanceteContext:
    """
    Container para todos os dados necessários para geração do balancete
    """

    request: HttpRequest
    form: BalanceteForm
    tipo_balancete: Literal["ECF", "DOMINIO"]
    data_inicial: date
    data_final: date
    df_empresas: pd.DataFrame
    empresas: Union[str, List[str]]
    conexao: Engine
    mostrar_conferencia: bool
    mostrar_resumo: bool
    transferencia: bool
    zeramento: bool
    cruzamento_ecf: bool
    consolidado: bool

    balancete: pd.DataFrame = field(default_factory=pd.DataFrame, repr=False)
    resumo_balancete: pd.DataFrame = field(default_factory=pd.DataFrame, repr=False)

    nome_empresa: Optional[str] = None
    cnpj: Optional[str] = None
    codigo_empresa: Optional[int] = None

    def __post_init__(self):
        """Inicializa campos derivados após a criação do objeto."""
        if len(self.df_empresas) == 1:
            self._inicializar_dados_empresa()

    @property
    def balancete_dict(self) -> Optional[list[dict]]:
        """
        Converte o DataFrame do balancete em lista de dicionários
        (orient='records'), pronta para exibir no template.
        """
        if not self.balancete.empty and isinstance(self.balancete, pd.DataFrame):
            return self.balancete.to_dict(orient="records")
        return None

    @property
    def resumo_balancete_dict(self) -> Optional[list[dict]]:
        """
        Converte o DataFrame de resumo em lista de dicionários
        (orient='records'), pronta para exibir no template.
        """
        if not self.resumo_balancete.empty and isinstance(
            self.resumo_balancete, pd.DataFrame
        ):
            return self.resumo_balancete.to_dict(orient="records")
        return None

    def _inicializar_dados_empresa(self) -> None:
        empresa_data = self.df_empresas.loc[0]
        self.nome_empresa = empresa_data.get("nome_emp")
        self.cnpj = empresa_data.get("CNPJ")
        self.codigo_empresa = empresa_data.get("codi_emp")


# Classe de erro
class BalanceteEmptyError(Exception):
    """Exceção lançada quando nenhum balancete é gerado."""

    def __init__(self, message: str = "Sem dados para emitir !"):
        super().__init__(message)


class Balancete:
    """
    Classe para geração de balancetes contábeis em diferentes formatos.

    Tipos disponíveis:
    - 'ECF': Formato para Escrituração Contábil Fiscal
    - 'DOMINIO': Formato padrão do sistema Domínio
    """

    @staticmethod
    def gerar(params: BalanceteContext) -> pd.DataFrame:
        """
        Gera um balancete contábil no formato especificado, para uma ou mais empresas.

        Parâmetros:
        -----------
        tipo : str
            Tipo de balancete a ser gerado ('ECF' ou 'DOMINIO')
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
        cruzamento_ecf : bool, optional
            Apenas para tipo 'DOMINIO'. Indica se deve incluir cruzamento com ECF (padrão: False)
        consolidado : bool, optional
            Indica se os resultados devem ser consolidados em um único DataFrame (padrão: True).
            Se False, retorna uma lista de DataFrames (um por empresa).

        Retorna:
        --------
        pd.DataFrame ou List[pd.DataFrame]
            DataFrame(s) com o(s) balancete(s) gerado(s)
        """
        if params.consolidado and params.tipo_balancete != "ECF":
            raise ValueError("A consolidação só está disponível para o tipo ECF")

        # Gera uma lista
        lista_codigos_empresas = (
            [params.empresas]
            if isinstance(params.empresas, str)
            else params.empresas.copy()
        )

        lista_balancetes = []

        for codigo_empresa in lista_codigos_empresas:
            if params.tipo_balancete == "ECF":
                df_balancete = Balancete._gerar_ecf(
                    empresa=codigo_empresa,
                    data_inicial=params.data_inicial,
                    data_final=params.data_final,
                    zeramento=params.zeramento,
                    transferencia=params.transferencia,
                    conexao=params.conexao,
                )
            elif params.tipo_balancete == "DOMINIO":
                df_balancete = Balancete._gerar_dominio(
                    empresa=codigo_empresa,
                    data_inicial=params.data_inicial,
                    data_final=params.data_final,
                    zeramento=params.zeramento,
                    transferencia=params.transferencia,
                    conexao=params.conexao,
                    cruzamento_ecf=params.cruzamento_ecf,
                )
            else:
                raise ValueError(
                    f"Tipo de balancete inválido: {params.tipo_balancete}. Use 'ECF' ou 'DOMINIO'"
                )

            if df_balancete.empty:
                continue

            if not params.consolidado:
                df_balancete.insert(0, "Cód. Empresa", codigo_empresa)

            lista_balancetes.append(df_balancete)

        if not lista_balancetes:
            raise BalanceteEmptyError()

        df_resultado = pd.concat(lista_balancetes, ignore_index=True)

        if params.consolidado:
            df_resultado = Balancete._consolidar_balancete(df_resultado)

        return df_resultado

    @staticmethod
    def _gerar_ecf(
        empresa: str,
        data_inicial: date,
        data_final: date,
        zeramento: bool,
        transferencia: bool,
        conexao: Engine,
    ) -> pd.DataFrame:
        """Gera balancete no formato ECF"""
        zeramento_param = "S" if zeramento else "N"
        transferencia_param = "S" if transferencia else "N"
        data_inicial_params = data_inicial.strftime("%Y-%m-%d")
        data_final_params = data_final.strftime("%Y-%m-%d")

        params = {
            "codi_emp": empresa,
            "data_inicial": data_inicial_params,
            "data_final": data_final_params,
            "zeramento": zeramento_param,
            "transferencia": transferencia_param,
        }

        # Consultas
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

        # Junta os resultados
        balancete = (
            resultadoContasECF.merge(
                resultadoDebitoAtual, on="contaLancamento", how="left"
            )
            .merge(resultadoCreditoAtual, on="contaLancamento", how="left")
            .merge(resultadoDebitoAnterior, on="contaLancamento", how="left")
            .merge(resultadoCreditoAnterior, on="contaLancamento", how="left")
        )

        # Processamento comum
        balancete = Balancete._processar_balancete(balancete, formato="ECF")

        return balancete

    @staticmethod
    def _gerar_dominio(
        empresa: str,
        data_inicial: date,
        data_final: date,
        zeramento: bool,
        transferencia: bool,
        conexao: Engine,
        cruzamento_ecf: bool,
    ) -> pd.DataFrame:
        """Gera balancete no formato Domínio"""
        zeramento_param = "S" if zeramento else "N"
        transferencia_param = "S" if transferencia else "N"
        data_inicial_params = data_inicial.strftime("%Y-%m-%d")
        data_final_params = data_final.strftime("%Y-%m-%d")

        params = {
            "codi_emp": empresa,
            "data_inicial": data_inicial_params,
            "data_final": data_final_params,
            "zeramento": zeramento_param,
            "transferencia": transferencia_param,
        }

        # Consultas
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

        # Junta os resultados
        balancete = (
            resultadoContasDominio.merge(
                resultadoDebitoAtual, on="contaLancamento", how="left"
            )
            .merge(resultadoCreditoAtual, on="contaLancamento", how="left")
            .merge(resultadoDebitoAnterior, on="contaLancamento", how="left")
            .merge(resultadoCreditoAnterior, on="contaLancamento", how="left")
        )

        # Processamento comum
        balancete = Balancete._processar_balancete(balancete, formato="DOMINIO")

        if cruzamento_ecf:
            balancete = Balancete._adicionar_cruzamento_ecf(balancete, params, conexao)

        return balancete

    @staticmethod
    def _processar_balancete(
        balancete: pd.DataFrame, formato: Literal["ECF", "DOMINIO"]
    ) -> pd.DataFrame:
        """Processamento comum para ambos os formatos de balancete"""
        # Preenche valores nulos com 0
        colunas_numericas = [
            "debitoAnterior",
            "credito_atual",
            "debito_atual",
            "creditoAnterior",
        ]
        for col in colunas_numericas:
            if col in balancete.columns:
                balancete[col] = pd.to_numeric(balancete[col], errors="coerce").fillna(
                    0
                )

        # Calcula saldos
        balancete["saldo_anterior"] = (
            balancete["debitoAnterior"] - balancete["creditoAnterior"]
        )
        balancete = balancete.drop(["debitoAnterior", "creditoAnterior"], axis=1)
        balancete["saldo_atual"] = (
            balancete["saldo_anterior"]
            + balancete["debito_atual"]
            - balancete["credito_atual"]
        )

        # Processa contas sintéticas
        analiticas = balancete[balancete["tipoConta"] == "A"].copy()

        for i, linha in balancete.iterrows():
            if linha["tipoConta"] == "S":
                classificacao_sintetica = linha["classificacaoConta"]
                contas_analiticas = analiticas[
                    analiticas["classificacaoConta"].str.startswith(
                        classificacao_sintetica
                    )
                ]

                soma_debito = contas_analiticas["debito_atual"].sum()
                soma_credito = contas_analiticas["credito_atual"].sum()
                saldo_anterior = contas_analiticas["saldo_anterior"].sum()
                saldo_atual = saldo_anterior + soma_debito - soma_credito

                balancete.loc[i, "credito_atual"] = soma_credito
                balancete.loc[i, "debito_atual"] = soma_debito
                balancete.loc[i, "saldo_anterior"] = saldo_anterior
                balancete.loc[i, "saldo_atual"] = saldo_atual

        # Filtra contas sem movimento
        balancete = balancete[
            (balancete["debito_atual"] != 0)
            | (balancete["credito_atual"] != 0)
            | (balancete["saldo_anterior"] != 0)
            | (balancete["saldo_atual"] != 0)
        ]

        # Ordena por classificação
        balancete.sort_values("classificacaoConta", inplace=True)

        # Formata classificação conforme o formato
        if formato == "ECF":
            balancete["classificacaoConta"] = balancete["classificacaoConta"].apply(
                regraClassificacaoECF
            )
        else:
            balancete["classificacaoConta"] = balancete["classificacaoConta"].apply(
                regraClassificacaoDominio
            )

        # Arredonda valores
        colunas_valores = [
            "saldo_anterior",
            "debito_atual",
            "credito_atual",
            "saldo_atual",
        ]
        balancete[colunas_valores] = balancete[colunas_valores].round(2)

        return balancete

    @staticmethod
    def _adicionar_cruzamento_ecf(
        balancete: pd.DataFrame, params: dict, conexao: Engine
    ) -> pd.DataFrame:
        """Adiciona informações de cruzamento com ECF ao balancete Domínio"""
        # Consultas para cruzamento
        relacao_credito = sql_para_dataframe(
            "dominio/balancete/normal/lancamentosCreditoNormal_Referencial.sql",
            conexao,
            params=params,
        )
        relacao_debito = sql_para_dataframe(
            "dominio/balancete/normal/lancamentosDebitoNormal_Referencial.sql",
            conexao,
            params=params,
        )
        resultadoContasECF = sql_para_dataframe(
            "dominio/balancete/ECF/contasECF.sql", conexao
        )

        # Unifica relações
        relacao_unificada = (
            pd.concat([relacao_credito, relacao_debito])
            .drop_duplicates(["contaLancamento", "contaLancamento_ECF"])
            .reset_index(drop=True)
        )

        # Renomeia colunas ECF
        resultadoContasECF.rename(
            columns={
                "contaLancamento": "contaLancamento_ECF",
                "classificacaoConta": "classificacaoConta_ECF",
                "descricaoConta": "descricaoConta_ECF",
                "tipoConta": "tipoConta_ECF",
            },
            inplace=True,
        )

        # Adiciona classificação ECF
        relacao_com_classificacao = relacao_unificada.merge(
            resultadoContasECF[
                ["contaLancamento_ECF", "classificacaoConta_ECF", "descricaoConta_ECF"]
            ],
            on="contaLancamento_ECF",
            how="left",
        ).drop(columns=["contaLancamento_ECF"])

        # Preenche valores vazios
        relacao_com_classificacao = relacao_com_classificacao.fillna("")

        # Agrupa por conta
        agrupado = (
            relacao_com_classificacao.groupby("contaLancamento")
            .agg({"descricaoConta_ECF": list, "classificacaoConta_ECF": list})
            .reset_index()
        )

        # Processa dados agrupados
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

        # Formata classificação ECF
        agrupado["classificacaoConta_ECF"] = agrupado["classificacaoConta_ECF"].apply(
            lambda lst: [regraClassificacaoECF(x) for x in lst] if lst else lst
        )

        # Simplifica quando há apenas um elemento
        agrupado["classificacaoConta_ECF"] = agrupado["classificacaoConta_ECF"].apply(
            lambda l: "" if not l else (l[0] if len(l) == 1 else l)
        )
        agrupado["descricaoConta_ECF"] = agrupado["descricaoConta_ECF"].apply(
            lambda l: "" if not l else (l[0] if len(l) == 1 else l)
        )

        # Conta referências
        agrupado["Qtd_Ref"] = (
            agrupado["classificacaoConta_ECF"]
            .apply(lambda x: len(x) if isinstance(x, list) else 1)
            .astype(str)
        )

        # Junta com o balancete
        balancete_com_ref = pd.merge(
            balancete, agrupado, on="contaLancamento", how="left"
        )

        # Filtra contas analíticas com movimento
        balancete_com_ref_analiticas = balancete_com_ref[
            (balancete_com_ref["tipoConta"] == "A")
            & (
                (balancete_com_ref["debito_atual"] > 0)
                | (balancete_com_ref["credito_atual"] > 0)
            )
        ].copy()

        # Adiciona colunas DC (Débito/Crédito)
        balancete_com_ref_analiticas["DC S.Ant."] = balancete_com_ref_analiticas[
            "saldo_anterior"
        ].apply(lambda x: "D" if x > 0 else ("C" if x < 0 else ""))
        balancete_com_ref_analiticas["DC S.Atual"] = balancete_com_ref_analiticas[
            "saldo_atual"
        ].apply(lambda x: "D" if x > 0 else ("C" if x < 0 else ""))

        # Valores absolutos para saldos
        balancete_com_ref_analiticas["saldo_anterior"] = balancete_com_ref_analiticas[
            "saldo_anterior"
        ].abs()
        balancete_com_ref_analiticas["saldo_atual"] = balancete_com_ref_analiticas[
            "saldo_atual"
        ].abs()

        # Renomeia colunas
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

        # Ordena colunas
        colunas_ordenadas = [
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

        return balancete_com_ref_analiticas[colunas_ordenadas]

    @staticmethod
    def _consolidar_balancete(balancete: pd.DataFrame) -> pd.DataFrame:
        """
        Consolida o balancete somando os valores por conta contábil.

        Parâmetros:
        -----------
        balancete : pd.DataFrame
            DataFrame com os dados do balancete

        Retorna:
        --------
        pd.DataFrame
            DataFrame consolidado
        """
        colunas_agrupamento = [
            "contaLancamento",
            "classificacaoConta",
            "descricaoConta",
            "tipoConta",
        ]

        # Colunas numéricas para soma
        colunas_numericas = [
            "debitoAnterior",
            "creditoAnterior",
            "debito_atual",
            "credito_atual",
            "saldo_anterior",
            "saldo_atual",
        ]

        # Filtra apenas colunas existentes no DataFrame
        colunas_agrupamento = [c for c in colunas_agrupamento if c in balancete.columns]
        colunas_numericas = [c for c in colunas_numericas if c in balancete.columns]

        # Agrupa e soma
        balancete_consolidado = (
            balancete.groupby(colunas_agrupamento, as_index=False)
            .agg({col: "sum" for col in colunas_numericas})
            .sort_values("classificacaoConta")
        )

        return balancete_consolidado
