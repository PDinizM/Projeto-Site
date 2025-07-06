from typing import Any, Dict

from .context import BalanceteContext
from .report import BalanceteReportResult


def montar_contexto(
    context: BalanceteContext, result: BalanceteReportResult
) -> Dict[str, Any]:
    empresa_info = context.df_empresas.loc[0]

    return {
        "form_title": context.form.titulo,
        "data_inicial": context.data_inicial,
        "data_final": context.data_final,
        "mostrar_resumo": context.mostrar_resumo,
        "mostrar_conferencia": context.mostrar_conferencia,
        "cnpj": empresa_info["CNPJ"],
        "codigo_empresa": empresa_info["codi_emp"],
        "nome_empresa": empresa_info["nome_emp"],
        "balancete": result.df_balancete.to_dict("records"),
        "resumo": (
            result.df_resumo.to_dict("records")
            if result.df_resumo is not None
            else None
        ),
    }
