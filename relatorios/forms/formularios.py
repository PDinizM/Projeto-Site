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
        help_text="Informe uma lista de empresas separada por vírgulas (Ex: 1,2,3).",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "pattern": "[0-9]*",
                "placeholder": "Digite apenas números",
            }
        ),
    )

    data_inicial = forms.DateField(
        label="Data Inicial",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )

    data_final = forms.DateField(
        label="Data Final",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True,
    )

    emitir_varias_empresas = forms.BooleanField(
        label="Emitir várias empresas",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
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

        if data_final < data_inicial:
            self.add_error(
                "data_final", "A data final não pode ser menor que a data inicial."
            )

    def _validar_empresas(self, data: dict) -> None:
        """
        Valida se as empresas existem
        """
        codigo_empresa = data.get("codigo_empresa")
        conexao = data.get("conexao")

        # Remove espaços, ignora vazios e garante unicidade
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
        self._varias_empresas = len(lista_empresas) > 1

    # Métodos utilitários para acesso aos dados validados (Poderia acessar-los diretamente, porém isso nao é o recomendado)
    def get_lista_empresas(self) -> list[str]:
        return self._lista_empresas

    def get_empresas_dataframe(self) -> pd.DataFrame:
        return self._df_empresas

    def is_varias_empresas(self) -> bool:
        return self._varias_empresas


# FORM ESPECIFICO DO BALANCETE, HERDA OS INPUTS DA BASE E INCREMENTA OS PROPRIOS.
class BalanceteForm(BasePesquisaForm):
    titulo = "Balancete"

    # Tipos de Balancete
    TIPOS_BALANCETE = [
        ("normal", "Balancete Normal"),
        ("plano_referencial", "Balancete Plano Referencial"),
    ]

    # Fields

    # Field Tipo Balancete
    balancete_tipo = forms.ChoiceField(
        choices=TIPOS_BALANCETE,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Tipo de Balancete",
        initial="normal",
    )

    # FIELDS OPÇÕES

    # Field Zeramento
    zeramento = forms.BooleanField(
        label="Desconsiderar Zeramento",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    # Field Transferencia
    transferencia = forms.BooleanField(
        label="Desconsiderar Transferência De Lucro/Prejuízo",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    consolidado = forms.BooleanField(
        label="Emitir Balancete Consolidado",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    conferencia = forms.BooleanField(
        label="Emitir Coluna Conferência",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    resumo = forms.BooleanField(
        label="Emitir Resumo Final",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    cruzamento_ecf = forms.BooleanField(
        label="Cruzamento Plano ECF",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        self._validar_consolidado_e_varias_empresas(cleaned_data)
        return cleaned_data

    def _validar_consolidado_e_varias_empresas(self, data: dict) -> None:
        """
        Valida se a pessoa mandou só 1 empresa quando deveria ser uma lista de empresas e vice-versa.
        """
        consolidado = data.get("consolidado", False)
        emitir_varias = data.get("emitir_varias_empresas", False)
        varias_empresas = self.is_varias_empresas()

        if (consolidado or emitir_varias) and not varias_empresas:
            self.add_error(
                "codigo_empresa",
                "Para gerar relatório consolidado ou múltiplas empresas, é necessário informar pelo menos duas empresas distintas.",
            )

        elif varias_empresas and not (consolidado or emitir_varias):
            self.add_error(
                "codigo_empresa",
                "Por favor, selecione a opção de relatório consolidado ou múltiplas empresas ao informar mais de uma empresa.",
            )
