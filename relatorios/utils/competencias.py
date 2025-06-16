from datetime import datetime
from dateutil.relativedelta import relativedelta

def obter_intervalo_meses(data_inicial, data_final):
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
    data_final = datetime.strptime(data_final, "%Y-%m-%d")

    intervalo = []
    atual = data_inicial.replace(day=1)

    while atual <= data_final:
        fim_mes = atual + relativedelta(day=31)
        if fim_mes > data_final:
            fim_mes = data_final

        intervalo.append([
            atual.strftime("%m/%Y"),
            atual.strftime("%Y-%m-%d"),
            fim_mes.strftime("%Y-%m-%d")
        ])
        atual += relativedelta(months=1)

    return intervalo


def formata_data(data, formato_atual, formato_desejado):
    return datetime.strptime(data, formato_atual).strftime(formato_desejado)

