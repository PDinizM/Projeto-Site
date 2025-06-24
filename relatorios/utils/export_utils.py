from io import BytesIO
from django.http import HttpResponse
import pandas as pd

def dataframe_para_excel_response(df: pd.DataFrame, nome_arquivo='arquivo.xlsx', nome_aba="Relatório") -> HttpResponse:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=nome_aba)
    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={nome_arquivo}'
    return response
