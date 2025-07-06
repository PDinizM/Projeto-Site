from datetime import date, datetime
from typing import Iterator, Tuple

from dateutil.relativedelta import relativedelta


def obter_intervalo_meses(
    data_inicial: date,
    data_final: date,
    formato_mes_ano: str = "%m/%Y",
    formato_data: str = "%Y-%m-%d",
) -> Iterator[Tuple[str, str, str]]:
    """
    Gera intervalos mensais entre duas datas como um iterador de tuplas formatadas.

    Melhorias implementadas:
    1. Uso de generator para economia de memória com grandes intervalos
    2. Cálculo mais preciso do último dia do mês
    3. Tratamento otimizado de meses incompletos
    4. Pré-validação mais rigorosa das datas

    Args:
        data_inicial: Data inicial do período
        data_final: Data final do período
        formato_mes_ano: Formato para exibição do mês/ano. Padrão: "%m/%Y"
        formato_data: Formato para as datas de início/fim. Padrão: "%Y-%m-%d"

    Returns:
        Iterador de tuplas (mês/ano, primeiro_dia, último_dia) formatados

    Raises:
        ValueError: Se data_inicial > data_final ou datas são inválidas

    Example:
        >>> list(obter_intervalo_meses(date(2023, 1, 15), date(2023, 3, 20)))
        [
            ('01/2023', '2023-01-01', '2023-01-31'),
            ('02/2023', '2023-02-01', '2023-02-28'),
            ('03/2023', '2023-03-01', '2023-03-20')
        ]
    """
    # Validação robusta das datas
    if not isinstance(data_inicial, date) or not isinstance(data_final, date):
        raise TypeError("As datas devem ser do tipo datetime.date")

    if data_inicial > data_final:
        raise ValueError("data_inicial deve ser anterior ou igual a data_final")

    current = data_inicial.replace(day=1)
    last_day_cache = {}  # Cache para cálculo do último dia do mês

    while current <= data_final:
        # Obtém o último dia do mês (com cache)
        month_key = (current.year, current.month)
        if month_key not in last_day_cache:
            next_month = current + relativedelta(months=1)
            last_day = next_month - relativedelta(days=1)
            last_day_cache[month_key] = last_day

        last_day_of_month = last_day_cache[month_key]
        end_date = min(last_day_of_month, data_final)

        yield (
            current.strftime(formato_mes_ano),
            current.strftime(formato_data),
            end_date.strftime(formato_data),
        )

        # Avança para o próximo mês
        try:
            current = last_day_of_month + relativedelta(days=1)
        except OverflowError:
            break


def formata_data(data, formato_atual, formato_desejado):
    return (
        datetime.strptime(data, formato_atual).strftime(formato_desejado)
        if isinstance(data, str)
        else data.strftime(formato_desejado)
    )
