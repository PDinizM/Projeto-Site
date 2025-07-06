from django import forms

from .base import BasePesquisaForm


class ComparativoForm(BasePesquisaForm):
    titulo = "Comparativo"

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

    # Field Saldo Anterior
    saldo_anterior = forms.BooleanField(
        label="Desconsiderar Saldo Anterior",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    # Field Saldo Acumulado
    saldo_acumulado = forms.BooleanField(
        label="Desconsiderar Saldo Acumulado",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    resumo = forms.BooleanField(
        label="Emitir Resumo Final",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    classificacoes = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="",
    )
