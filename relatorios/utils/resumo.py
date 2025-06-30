from typing import Dict, List, Optional

import pandas as pd


class Resumo:
    def __init__(
        self, balancete: pd.DataFrame, classificacoes_contas: Optional[List[str]] = None
    ):
        """
        Classe para geração de resumos de balancetes contábeis.

        Args:
            balancete: DataFrame com os dados do balancete
            classificacoes_contas: Lista de classificações de contas a considerar (padrão: ['1', '2', '3', '4'])
        """
        self.balancete = balancete
        self.classificacoes = classificacoes_contas or ["1", "2", "3", "4"]
        self.df_resumo = self._filtrar_contas()

    def _filtrar_contas(self) -> pd.DataFrame:
        """Filtra as contas conforme as classificações especificadas."""
        return self.balancete[
            self.balancete["classificacaoConta"].isin(self.classificacoes)
        ].copy()

    def _calcular_totais(self, classificacoes: List[str]) -> pd.Series:
        """Calcula totais para um grupo de classificações de contas."""
        return self.df_resumo[
            self.df_resumo["classificacaoConta"].isin(classificacoes)
        ][["debito_atual", "credito_atual", "saldo_anterior", "saldo_atual"]].sum()

    def _calcular_resultado_mes(self) -> Dict[str, float]:
        """Calcula o resultado do mês conforme regras contábeis."""
        contas_4 = self.df_resumo[self.df_resumo["classificacaoConta"] == "4"]
        contas_3 = self.df_resumo[self.df_resumo["classificacaoConta"] == "3"]

        credito_atual = contas_3["credito_atual"].sum() - contas_3["debito_atual"].sum()
        debito_atual = contas_4["credito_atual"].sum() - contas_4["debito_atual"].sum()

        return {
            "debito_atual": abs(debito_atual),
            "credito_atual": abs(credito_atual),
            "saldo_anterior": 0,
            "saldo_atual": (credito_atual + debito_atual) * -1,
        }

    def _calcular_resultado_exercicio(self) -> Dict[str, float]:
        """Calcula o resultado do exercício conforme regras contábeis."""
        contas_4 = self.df_resumo[self.df_resumo["classificacaoConta"] == "4"]
        contas_3 = self.df_resumo[self.df_resumo["classificacaoConta"] == "3"]

        saldo_anterior = (
            contas_4["saldo_anterior"].sum() + contas_3["saldo_anterior"].sum()
        )
        debito_atual = contas_4["saldo_atual"].sum()
        credito_atual = contas_3["saldo_atual"].sum()

        return {
            "debito_atual": abs(debito_atual),
            "credito_atual": abs(credito_atual),
            "saldo_anterior": saldo_anterior,
            "saldo_atual": debito_atual + credito_atual,
        }

    def _criar_linha_resumo(self, descricao: str, dados: Dict) -> Dict:
        """Cria um dicionário representando uma linha de resumo."""
        return {
            "contaLancamento": "",
            "classificacaoConta": "",
            "descricaoConta": descricao,
            "tipoConta": "",
            **dados,
        }

    def gerar(self) -> pd.DataFrame:
        """Gera o DataFrame completo com o resumo do balancete."""
        # Calcula totais devedores e credores
        devedoras = self._calcular_totais(["1", "4"])
        credoras = self._calcular_totais(["2", "3"])

        # Calcula resultados
        resultado_mes = self._calcular_resultado_mes()
        resultado_exercicio = self._calcular_resultado_exercicio()

        # Cria linhas extras
        linhas_extra = [
            self._criar_linha_resumo("CONTAS DEVEDORAS", devedoras),
            self._criar_linha_resumo("CONTAS CREDORAS", credoras),
            self._criar_linha_resumo("RESULTADO DO MÊS", resultado_mes),
            self._criar_linha_resumo("RESULTADO DO EXERCÍCIO", resultado_exercicio),
        ]

        # Combina tudo em um único DataFrame
        return pd.concat(
            [self.df_resumo, pd.DataFrame(linhas_extra)], ignore_index=True
        )

    @property
    def to_dict(self) -> Dict:
        """Retorna os resultados principais como dicionário para templates."""
        return {
            "devedoras": self._calcular_totais(["1", "4"]).to_dict(),
            "credoras": self._calcular_totais(["2", "3"]).to_dict(),
            "resultado_mes": self._calcular_resultado_mes(),
            "resultado_exercicio": self._calcular_resultado_exercicio(),
        }
