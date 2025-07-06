from dataclasses import dataclass
from datetime import date
from typing import List, Literal, Union

import pandas as pd
from django.http import HttpRequest
from sqlalchemy.engine import Engine

from relatorios.forms.balancete import BalanceteForm


@dataclass(slots=True)
class BalanceteContext:
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


class BalanceteEmptyError(Exception):
    """Exceção lançada quando nenhum balancete é gerado."""

    def __init__(self, message: str = "Sem dados para emitir !"):
        super().__init__(message)
