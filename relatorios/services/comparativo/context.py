from dataclasses import dataclass
from datetime import date
from typing import List, Union

import pandas as pd
from django.http import HttpRequest
from sqlalchemy.engine import Engine

from relatorios.forms.comparativo import ComparativoForm


@dataclass(slots=True)
class ComparativoContext:
    request: HttpRequest
    form: ComparativoForm
    data_inicial: date
    data_final: date
    df_empresas: pd.DataFrame
    empresas: Union[str, List[str]]
    conexao: Engine
    mostrar_resumo: bool
    transferencia: bool
    zeramento: bool
    saldo_anterior: bool
    saldo_acumulado: bool
    classificacoes: List[str]


class ComparativoEmptyError(Exception):
    """Exceção lançada quando nenhum balancete é gerado."""

    def __init__(self, message: str = "Sem dados para emitir !"):
        super().__init__(message)
