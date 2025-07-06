from dataclasses import dataclass

import pandas as pd
from django.http import HttpResponse

from relatorios.utils.export_utils import dataframe_para_excel_response
from relatorios.utils.resumo import Resumo

from .context import ComparativoContext
from .generator import Comparativo


@dataclass(slots=True)
class ComparativoReportResult:
    df_comparativo: pd.DataFrame
    df_resumo: pd.DataFrame | None
    excel_response: HttpResponse | None


class ComparativoReportService:
    """Orquestra a geração do balancete, resumo e exportação."""

    @staticmethod
    def gerar(context: ComparativoContext) -> ComparativoReportResult:
        df_comparativo = Comparativo.gerar(context)

        df_resumo = Resumo(df_comparativo).gerar() if context.mostrar_resumo else None

        excel_response = (
            dataframe_para_excel_response(
                df_comparativo, "Comparativo.xlsx", "Comparativo"
            )
            if ComparativoReportService._should_export_excel(context)
            else None
        )

        return ComparativoReportResult(df_comparativo, df_resumo, excel_response)

    @staticmethod
    def _should_export_excel(context: ComparativoContext) -> bool:
        return len(context.empresas) > 1
