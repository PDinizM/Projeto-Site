from django import forms

from .base import BasePesquisaForm


class RazaoForm(BasePesquisaForm):
    titulo = "Razão"
    # Fields

    conta = forms.IntegerField(
        label="Selecionar conta para emissão",
    )

    totalizador_conta = forms.BooleanField(
        label="Totalizar por conta",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    totalizador_mes = forms.BooleanField(
        label="Totalizar por mês",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    totalizador_dia = forms.BooleanField(
        label="Totalizar por dia",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    descricao_contrapartida = forms.BooleanField(
        label="Emitir a descrição das contas de contrapartida",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    omitir_saldo = forms.BooleanField(
        label="Omitir coluna Saldo",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    omitir_saldo_exercicio = forms.BooleanField(
        label="Omitir coluna Saldo",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
