from dataclasses import dataclass
from typing import Any, Callable, List

import pandas as pd
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from sqlalchemy.engine import Engine

from relatorios.forms.formularios import BalanceteForm
from relatorios.utils.balancete_utils import (
    gerar_balancete,
    relatorioBalanceteDominio,
    relatorioBalanceteECF,
)
from relatorios.utils.competencias import formata_data
from relatorios.utils.conexao import conectar_dominio
from relatorios.utils.export_utils import dataframe_para_excel_response


@dataclass
class BalanceteContexto:
    request: HttpRequest
    form: BalanceteForm
    tipo_balancete: str
    data_inicial: str
    data_final: str
    transferencia: bool
    zeramento: bool
    cruzamento_ecf: bool
    consolidado: bool
    emitir_varias_empresas: bool
    varias_empresas: bool
    mostrar_conferencia: bool
    mostrar_resumo: bool
    df_empresas: pd.DataFrame
    lista_empresas: List[str]
    conexao: Engine


def balancete_relatorio_view(request: HttpRequest) -> HttpResponse:
    # SE FOR GET PEGA MEU FORMULARIO CRIADO, SE FOR POST MANDA MEU FORMULARIO PARA AS VALIDAÇÕES.

    form = BalanceteForm() if request.method == "GET" else BalanceteForm(request.POST)

    # SE FOR GET, RENDERIZA O FORMULARIO SE FOR POST E NAO FOR ERRO RENDERIZA O FORMULARIO COM ERRO.
    if request.method == "GET" or not form.is_valid():
        return _renderizar_formulario_balancete(request, form)

    """
    Após a validação do formulário, os dados são extraídos e encapsulados em um único objeto (BalanceteContexto).

    Essa abordagem facilita a reutilização dos dados em funções auxiliares e handlers, evita repetição de código,
    reduz dependências de escopo, melhora a tipagem e torna o código mais limpo, organizado e de fácil manutenção.
    """
    dados = form.cleaned_data

    balancete_dados = BalanceteContexto(
        request=request,
        form=form,
        tipo_balancete=dados["balancete_tipo"],
        data_inicial=dados["data_inicial"],
        data_final=dados["data_final"],
        transferencia=dados.get("transferencia", False),
        zeramento=dados.get("zeramento", False),
        cruzamento_ecf=dados.get("cruzamento_ecf", False),
        consolidado=dados.get("consolidado", False),
        emitir_varias_empresas=dados.get("emitir_varias_empresas", False),
        mostrar_conferencia=dados.get("conferencia", False),
        mostrar_resumo=dados.get("resumo", False),
        df_empresas=form.get_empresas_dataframe(),
        lista_empresas=form.get_lista_empresas(),
        varias_empresas=form.is_varias_empresas(),
        conexao=conectar_dominio(dados["conexao"]),
    )

    if balancete_dados.consolidado:
        return _handle_consolidado(balancete_dados)

    if balancete_dados.emitir_varias_empresas or balancete_dados.cruzamento_ecf:
        return _handle_cruzamento_ecf(balancete_dados)

    return _handle_normal(balancete_dados)


####################################################################################################

# AQUI SÃO FUNÇÕES PRIVADAS, HANDLERS, NO INTUITO DE FRAGMENTAR O CÓDIGO E DEIXAR-LO MAIS ORGANIZADO.


def _renderizar_formulario_balancete(
    request: HttpRequest, form: BalanceteForm
) -> HttpResponse:
    """
    Renderiza o formulário,
    """

    return render(
        request,
        "relatorios/balancete/form.html",
        {"form": form, "form_title": form.titulo},
    )


def _criar_contexto_resultado(
    balancete_dados: BalanceteContexto,
    balancete: pd.DataFrame,
    resumo_balancete: pd.DataFrame | None = None,
) -> dict:
    """
    Monta o contexto para renderizar o relatório de balancete.
    """

    contexto = {
        "dados_relatorio_balancete": balancete.to_dict(orient="records"),
        "data_inicial": formata_data(
            balancete_dados.data_inicial, "%Y-%m-%d", "%d/%m/%Y"
        ),
        "data_final": formata_data(balancete_dados.data_final, "%Y-%m-%d", "%d/%m/%Y"),
        "mostrar_resumo": balancete_dados.mostrar_resumo,
        "mostrar_conferencia": balancete_dados.mostrar_conferencia,
        "varias_empresas": balancete_dados.varias_empresas,
        "cnpj": balancete_dados.df_empresas.loc[0, "CNPJ"],
        "nome_empresa": balancete_dados.df_empresas.loc[0, "nome_emp"],
        "form_title": balancete_dados.form.titulo,
        "lista_empresas": balancete_dados.lista_empresas,
    }

    if resumo_balancete is not None:
        contexto["dados_relatorio_resumo"] = resumo_balancete.to_dict(orient="records")

    return contexto


def _valida_balancete_vazio(
    balancete: pd.DataFrame, form: BalanceteForm, request: HttpRequest
) -> HttpResponse | None:
    """
    Verifica se o DataFrame do balancete está vazio.
    Se estiver, adiciona erro ao formulário e retorna a renderização com erro.
    Caso contrário, retorna None.
    """

    if balancete.empty:
        form.add_error(None, "Não há dados a serem mostrados.")
        return _renderizar_formulario_balancete(request, form)
    return None


def _gerar_balancetes_multiplas_empresas(
    empresas: List[str], func_geracao: Callable[[str, Any], pd.DataFrame], *args
) -> pd.DataFrame:
    dfs = []
    for empresa in empresas:
        df = func_geracao(empresa, *args)
        df.insert(0, "Empresa", empresa)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def _gerar_resumo_balancete(balancete: pd.DataFrame) -> pd.DataFrame:
    df_resumo = balancete[
        balancete["classificacaoConta"].isin(["1", "2", "3", "4"])
    ].copy()

    devedoras = df_resumo[df_resumo["classificacaoConta"].isin(["1", "4"])][
        ["debito_atual", "credito_atual", "saldo_anterior", "saldo_atual"]
    ].sum()

    credoras = df_resumo[df_resumo["classificacaoConta"].isin(["2", "3"])][
        ["debito_atual", "credito_atual", "saldo_anterior", "saldo_atual"]
    ].sum()

    resultado_mes = df_resumo[df_resumo["classificacaoConta"].isin(["3", "4"])][
        ["debito_atual", "credito_atual", "saldo_anterior", "saldo_atual"]
    ].sum()

    linhas_extra = pd.DataFrame(
        [
            {
                "contaLancamento": "",
                "classificacaoConta": "",
                "descricaoConta": "CONTAS DEVEDORAS",
                "tipoConta": "",
                **devedoras,
            },
            {
                "contaLancamento": "",
                "classificacaoConta": "",
                "descricaoConta": "CONTAS CREDORAS",
                "tipoConta": "",
                **credoras,
            },
            {
                "contaLancamento": "",
                "classificacaoConta": "",
                "descricaoConta": "RESULTADO DO EXERCÍCIO",
                "tipoConta": "",
                **resultado_mes,
            },
        ]
    )

    return pd.concat([df_resumo, linhas_extra], ignore_index=True)


# === HANDLERS ===


def _handle_normal(balancete_dados: BalanceteContexto) -> HttpResponse:
    """
    Gera e renderiza o balancete padrão de uma única empresa.
    """
    balancete = gerar_balancete(
        balancete_dados.tipo_balancete,
        balancete_dados.lista_empresas[0],
        balancete_dados.data_inicial,
        balancete_dados.data_final,
        balancete_dados.conexao,
        balancete_dados.zeramento,
        balancete_dados.transferencia,
        balancete_dados.cruzamento_ecf,
    )

    if res := _valida_balancete_vazio(
        balancete, balancete_dados.form, balancete_dados.request
    ):
        return res

    resumo_balancete = (
        _gerar_resumo_balancete(balancete) if balancete_dados.mostrar_resumo else None
    )

    contexto = _criar_contexto_resultado(balancete_dados, balancete, resumo_balancete)

    return render(balancete_dados.request, "relatorios/balancete/result.html", contexto)


def _handle_cruzamento_ecf(balancete_dados: BalanceteContexto) -> HttpResponse:
    """
    Gera o balancete com cruzamento ECF para uma ou múltiplas empresas e retorna um HttpResponse com arquivo Excel (.xlsx).
    """

    balancete = _gerar_balancetes_multiplas_empresas(
        balancete_dados.lista_empresas,
        relatorioBalanceteDominio,
        balancete_dados.data_inicial,
        balancete_dados.data_final,
        balancete_dados.zeramento,
        balancete_dados.transferencia,
        balancete_dados.conexao,
        balancete_dados.cruzamento_ecf,
    )

    if res := _valida_balancete_vazio(
        balancete, balancete_dados.form, balancete_dados.request
    ):
        return res

    return dataframe_para_excel_response(
        balancete, "Balancete x Cruzamento ECF.xlsx", "Cruzamento"
    )


def _handle_consolidado(balancete_dados: BalanceteContexto) -> HttpResponse:
    """
    Gera e renderiza o balancete ECF consolidado.
    """

    balancete = _gerar_balancetes_multiplas_empresas(
        balancete_dados.lista_empresas,
        relatorioBalanceteECF,
        balancete_dados.data_inicial,
        balancete_dados.data_final,
        balancete_dados.zeramento,
        balancete_dados.transferencia,
        balancete_dados.conexao,
    )

    if res := _valida_balancete_vazio(
        balancete, balancete_dados.form, balancete_dados.request
    ):
        return res

    balancete = (
        balancete.groupby(
            ["contaLancamento", "classificacaoConta", "descricaoConta", "tipoConta"],
            as_index=False,
        )
        .sum(numeric_only=True)
        .sort_values("classificacaoConta")
    )

    resumo_balancete = (
        _gerar_resumo_balancete(balancete) if balancete_dados.mostrar_resumo else None
    )

    contexto = _criar_contexto_resultado(balancete_dados, balancete, resumo_balancete)

    return render(balancete_dados.request, "relatorios/balancete/result.html", contexto)
