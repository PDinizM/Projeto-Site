from dataclasses import dataclass

import pandas as pd
from django.http import HttpResponse

from relatorios.utils.export_utils import dataframe_para_excel_response
from relatorios.utils.resumo import Resumo

from .context import BalanceteContext
from .generator import Balancete


@dataclass(slots=True)
class BalanceteReportResult:
    df_balancete: pd.DataFrame
    df_resumo: pd.DataFrame | None
    excel_response: HttpResponse | None


class BalanceteReportService:
    """Orquestra a geração do balancete, resumo e exportação."""

    @staticmethod
    def gerar(context: BalanceteContext) -> BalanceteReportResult:
        df_balancete = Balancete.gerar(context)

        df_resumo = Resumo(df_balancete).gerar() if context.mostrar_resumo else None

        excel_response = (
            dataframe_para_excel_response(df_balancete, "Balancete.xlsx", "Balancete")
            if BalanceteReportService._should_export_excel(context)
            else None
        )

        return BalanceteReportResult(df_balancete, df_resumo, excel_response)

    @staticmethod
    def _should_export_excel(context: BalanceteContext) -> bool:
        return (
            len(context.empresas) > 1 and not context.consolidado
        ) or context.cruzamento_ecf
