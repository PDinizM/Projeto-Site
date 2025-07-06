from typing import Any, Dict

from .context import ComparativoContext
from .report import ComparativoReportResult


def montar_contexto(
    context: ComparativoContext, result: ComparativoReportResult
) -> Dict[str, Any]:
    empresa_info = context.df_empresas.loc[0]

    todas_colunas = list(result.df_comparativo.keys())
    colunas_meses = todas_colunas[5:]  # Pega tudo depois da 3ª coluna

    return {
        "form_title": context.form.titulo,
        "data_inicial": context.data_inicial,
        "data_final": context.data_final,
        "mostrar_resumo": context.mostrar_resumo,
        "cnpj": empresa_info["CNPJ"],
        "codigo_empresa": empresa_info["codi_emp"],
        "nome_empresa": empresa_info["nome_emp"],
        "comparativo": result.df_comparativo.to_dict("records"),
        "meses_ordenados": colunas_meses,
        "resumo": (
            result.df_resumo.to_dict("records")
            if result.df_resumo is not None
            else None
        ),
    }
