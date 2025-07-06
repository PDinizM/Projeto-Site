import pandas as pd
from django import forms
from sqlalchemy import Integer

from relatorios.utils.conexao import CONEXOES_DOMINIO, conectar_dominio
from sql.utils.sql_utils import sql_para_dataframe


class BasePesquisaForm(forms.Form):
    """
    Formulário base para pesquisa de relatórios com conexão, empresas e datas.
    """

    conexao = forms.ChoiceField(
        choices=[(c, c) for c in CONEXOES_DOMINIO],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Conexão",
        required=True,
        initial="Banco 1",
    )

    codigo_empresa = forms.CharField(
        label="Empresa",
        required=True,
        help_text="Para multiplas empresas informe uma lista de empresas separada por vírgulas (Ex: 1,2,3).",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "x-on:input": "filtrarEmpresa($event)",
                "x-model": "codigo_empresa",
            }
        ),
    )

    data_inicial = forms.DateField(
        label="Data Inicial",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "max": "9999-12-31"}
        ),
        required=True,
    )

    data_final = forms.DateField(
        label="Data Final",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "max": "9999-12-31"}
        ),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        self._validar_datas(cleaned_data)
        self._validar_empresas(cleaned_data)
        return cleaned_data

    # 1º DATA FINAL NAO SEJA MENOR QUE A DATA INICIAL.
    def _validar_datas(self, data: dict) -> None:
        """
        Valida se data_final >= data_inicial.
        """
        data_inicial = data.get("data_inicial")
        data_final = data.get("data_final")

        if data_inicial and data_final and data_final < data_inicial:
            self.add_error(
                "data_final", "A data final não pode ser menor que a data inicial."
            )

    def _validar_empresas(self, data: dict) -> None:
        """
        Valida se as empresas existem
        """

        self._df_empresas = pd.DataFrame()
        self._lista_empresas = []
        codigo_empresa = data.get("codigo_empresa")
        conexao = data.get("conexao")

        # Remove espaços, ignora vazios e garante unicidade
        if not codigo_empresa or not codigo_empresa.strip():
            self.add_error("codigo_empresa", "Informe pelo menos uma empresa.")
            return

        lista_empresas = sorted(
            {e.strip() for e in codigo_empresa.split(",") if e.strip()}
        )

        conexao_db = conectar_dominio(conexao)

        df_empresas = sql_para_dataframe(
            "dominio/empresas.sql",
            conexao_db,
            {"lista_empresas": lista_empresas},
            {"lista_empresas": Integer},
        )

        conexao_db.dispose()

        encontrados = set(df_empresas["codi_emp"].astype(str))
        nao_encontrados = [e for e in lista_empresas if e not in encontrados]

        if nao_encontrados:
            msg = (
                f"A empresa {nao_encontrados[0]} não foi encontrada no banco de dados."
                if len(nao_encontrados) == 1
                else f"As seguintes empresas não foram encontradas: {', '.join(nao_encontrados)}"
            )
            self.add_error("codigo_empresa", msg)

        # Definir atributos para o meu formulário, permitindo que eu os recupere no futuro sem a necessidade de reconsultar ou revalidar.
        self._lista_empresas = lista_empresas
        self._df_empresas = df_empresas

    # Métodos utilitários para acesso aos dados validados (Poderia acessar-los diretamente, porém isso nao é o recomendado)
    def get_lista_empresas(self) -> list[str]:
        return self._lista_empresas

    def get_empresas_dataframe(self) -> pd.DataFrame:
        return self._df_empresas
