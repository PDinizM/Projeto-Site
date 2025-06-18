from django import forms
from django.core.exceptions import ValidationError


# FORM BASE (BOA PARTE DOS RELATORIOS PRECISAM DESSES INPUTS)

class BasePesquisaForm(forms.Form):
    
    # Conexões Possiveis
    
    CONEXOES = [
        ('Banco 1', 'Banco 1'),
        ('Banco 2', 'Banco 2'),
        ('Banco 3', 'Banco 3'),
        ('Banco 4', 'Banco 4'),
    ]

    # Fields 

    conexao = forms.ChoiceField(
        choices=CONEXOES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Conexão',
        required=True
    )
    
    empresa = forms.CharField(
        label='Empresa',
        help_text='Digite o código da empresa ou uma lista separada por vírgulas.',
        widget=forms.TextInput(attrs={'class': 'form-control'}
        ),
    )

    data_inicial = forms.DateField(
        label='Data Inicial',
        widget=forms.DateInput(attrs={'type': 'date', 'class':'form-control'}),
        error_messages={
            'required': 'Este campo é obrigatório.',
            'invalid': 'Digite uma data válida.'
        }
    )

    data_final = forms.DateField(
        label='Data Final',
        widget=forms.DateInput(attrs={'type': 'date','class':'form-control'}),
         error_messages={
            'required': 'Este campo é obrigatório.',
            'invalid': 'Digite uma data válida.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get('data_incial')
        data_final = cleaned_data.get('data_final')

        if data_inicial and data_final and data_final < data_inicial:
            raise ValidationError("A data final não pode ser menor que a data inicial.")

# # FORM ESPECIFICO DO BALANCETE, HERDA OS INPUTS DA BASE E INCREMENTA OS PROPRIOS.
#     def clean_empresa(self):
#             empresa = self.cleaned_data.get('empresa')
#             if empresa:
#                 # Remove espaços extras
#                 empresa = empresa.strip()
#                 if not empresa:
#                     raise ValidationError("Este campo é obrigatório.")
#             return empresa
        
#         def clean(self):
#             cleaned_data = super().clean()
#             data_inicial = cleaned_data.get('dataInicial')
#             data_final = cleaned_data.get('dataFinal')
            
#             if data_inicial and data_final and data_final < data_inicial:
#                 raise ValidationError("A data final não pode ser menor que a data inicial.")
            
#             return cleaned_data

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
        label='Tipo de Balancete',
        error_messages={
            'required': 'Selecione um tipo de balancete.',
            'invalid_choice': 'Selecione um tipo de balancete válido.'
        }
    )
    
    # Field Zeramento
    zeramento = forms.BooleanField(
        required=False,
        label='Desconsiderar Zeramento',
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    # Field Transferencia
    transferencia = forms.BooleanField(
        required=False,
        label='Desconsiderar Transferência De Lucro/Prejuízo',
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )
    
    # Field Resumo
    resumo = forms.BooleanField(
        required=False,
        label='Emitir Resumo',
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'})
    )