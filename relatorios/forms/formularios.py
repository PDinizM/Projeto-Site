from django import forms
from django.core.exceptions import ValidationError


# FORM BASE (BOA PARTE DOS RELATORIOS PRECISAM DESSES INPUTS)
class BasePesquisaForm(forms.Form):
    
    # Conexões Possiveis
    
    CONEXOES = [
        ('banco1', 'Banco 1'),
        ('banco2', 'Banco 2'),
        ('banco3', 'Banco 3'),
        ('banco4', 'Banco 4'),
    ]

    # Fields 

    conexao = forms.ChoiceField(
        choices=CONEXOES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Conexão'
    )
    
    empresa = forms.CharField(
        label='Empresa:',
        help_text='Digite o código da empresa ou uma lista separada por vírgulas.'
    )
    
    
    dataInicial = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    dataFinal = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get('dataInicial')
        data_final = cleaned_data.get('dataFinal')

        if data_inicial and data_final and data_final < data_inicial:
            raise ValidationError("A data final não pode ser menor que a data inicial.")

# FORM ESPECIFICO DO BALANCETE, HERDA OS INPUTS DA BASE E INCREMENTA OS PROPRIOS.
class BalanceteForm(BasePesquisaForm):

    # Tipos de Balancete
    
    TIPOS_BALANCETE = [
        ('normal', 'Balancete Normal'),
        ('plano_referencial', 'Balancete Plano Referencial'),
    ]
    
    # Fields
    
    # Field Tipo Balancete

    balancete_tipo = forms.ChoiceField(
        choices=TIPOS_BALANCETE,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Tipo de Balancete'
    )

    # Field Zeramento

    zeramento = forms.BooleanField(
        required=False,
        label='Desconsiderar Zeramento'
    )
    
    # Field Transferencia

    transferencia = forms.BooleanField(
        required=False,
        label='Desconsiderar Transferência De Lucro/Prejuízo'
    )
    
    # Field Resumo
    
    resumo = forms.BooleanField(
        required=False,
        label='Emitir Resumo'
    )
