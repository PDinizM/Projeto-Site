from django import forms

from .base import BasePesquisaForm


class BalanceteForm(BasePesquisaForm):
    titulo = "Balancete"

    # Tipos de Balancete
    TIPOS_BALANCETE = [
        ("DOMINIO", "Balancete Normal"),
        ("ECF", "Balancete Plano Referencial"),
    ]

    # Fields

    # Field Tipo Balancete
    balancete_tipo = forms.ChoiceField(
        choices=TIPOS_BALANCETE,
        widget=forms.RadioSelect(
            attrs={"class": "form-check-input", "x-model": "balancete_tipo"}
        ),
        label="Tipo de Balancete",
        initial="DOMINIO",
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
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "x-model": "consolidado"}
        ),
    )

    conferencia = forms.BooleanField(
        label="Emitir Coluna Conferência",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "x-model": "conferencia"}
        ),
    )

    resumo = forms.BooleanField(
        label="Emitir Resumo Final",
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "x-model": "resumo"}
        ),
    )

    cruzamento_ecf = forms.BooleanField(
        label="Cruzamento Plano ECF",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "x-model": "cruzamento_ecf",
                "@change": "aoAlterarCruzamento",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        self._validar_consolidado(cleaned_data)
        return cleaned_data

    def _validar_consolidado(self, data: dict) -> None:
        """
        Valida se a pessoa pediu para consolidar e mandou só 1 empresa
        """

        consolidado = data.get("consolidado", False)
        varias_empresas = True if len(self.get_empresas_dataframe()) > 1 else False

        if consolidado and not varias_empresas:
            self.add_error(
                "codigo_empresa",
                "Para gerar relatório consolidado, é necessário informar pelo menos duas empresas distintas.",
            )
