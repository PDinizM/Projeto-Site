from io import BytesIO

import pandas as pd
from django.http import HttpResponse


def dataframe_para_excel_response(
    df: pd.DataFrame, nome_arquivo="arquivo.xlsx", nome_aba="Relatório"
) -> HttpResponse:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    buffer.seek(0)

    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'
    response.set_cookie("download_complete", "true", max_age=60)
    return response
